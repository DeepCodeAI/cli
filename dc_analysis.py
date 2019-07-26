"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import json
import os
import sys
import webbrowser

import progressbar

import util
from api import Api, ApiException, ApiUnauthorizedException, ApiRequestBodyTooLarge, JobBundles

# maximum size of batch upload content in bytes, to avoid running into "payload too large" errors
# the API will add a a bit more because of overhead introduced by the json
MAX_BATCH_CONTENT_SIZE = 512000  # 512 kB
# files larger than this are not included in the bundle (not read from filesystem, not hashed, not uploaded)
MAX_FILE_SIZE = 256000  # 256 kB
PUBLIC_NOTICE = "LEGAL NOTICE\n" + \
                "------------\n" + \
                "You are logged into DeepCode with a public user account. Be aware that any code\n" + \
                "that you upload to DeepCode is treated as if it was a public repository.\n" + \
                "We do not protect your suggestions or code from other users.\n" + \
                "If you want your code to be protected against access form other users, please\n" + \
                "upgrade your account to a 'private' account at http://www.deepcode.ai.\n"


class DCAnalysis:
    def __init__(self, config, silent):
        self.config = config
        self.api = Api(config)
        self.silent = silent

    def _progress_bar(self, title, iterator, max_value=None):
        if self.silent:
            return iterator
        else:
            print(title)
            return progressbar.progressbar(iterator, max_value=max_value)

    def _redirect_std_out(self):
        if self.silent:
            self.original_stdout = sys.stdout
            f = open(os.devnull, 'w')
            sys.stdout = f

    def _restore_std_out(self):
        if self.silent:
            sys.stdout.close()
            sys.stdout = self.original_stdout

    def login(self):
        """
        Log into DeepCode
        throws DCAnalysisError if an error occurs
        :return: (private | public | string with login url)
        """
        try:
            res = self.api.check_login()
            if res.type:
                return res.type
            else:
                res = self.api.login()
                return res.login_url
        except ApiException as err:
            raise DCAnalysisError(err)

    def wait_for_login(self):
        """
        Wait for user to be logged in
        throws DCAnalysisError if an error occurs
        :return: (private | public)
        """
        try:
            res = self.api.wait_for_login()
            if res.type:
                return res
            else:
                raise DCAnalysisError('Unable to log in')
        except ApiException as err:
            raise DCAnalysisError(err)

    def logout(self):
        """
        Log out the current user
        """
        self.config.delete_session_token()

    def analyze(self, bundle):
        """
        Analyze and potentially upload the provided bundle
        :param bundle: either repo/owner[/commit] or local folder
        :return: suggestions
        """
        try:
            if not self.api.check_login().type:
                raise DCAnalysisError('Not logged in, please log in first')
            self._redirect_std_out()
            bundle_id = self._create_bundle(bundle)
            bundle = JobBundles(bundle_id)
            if not self.silent:
                print('analyzing...')
            return self.api.wait_for_analysis_state(bundle, 'DONE')
        except ApiException as err:
            raise DCAnalysisError(err)
        finally:
            self._restore_std_out()

    def diff(self, bundle1, bundle2):
        """
        Do diff analyze and potentially upload the provided bundles
        :param bundle1: either repo/owner[/commit] or local folder
        :param bundle2: either repo/owner[/commit] or local folder
        :return: suggestions
        """
        try:
            if not self.api.check_login().type:
                raise DCAnalysisError('Not logged in, please log in first')
            self._redirect_std_out()
            bundle_id1 = self._create_bundle(bundle1)
            bundle_id2 = self._create_bundle(bundle2)
            bundles = JobBundles(bundle_id1, bundle_id2)
            return self.api.wait_for_analysis_state(bundles, 'DONE')
        except ApiException as err:
            raise DCAnalysisError(err)
        finally:
            self._restore_std_out()

    def _create_bundle(self, bundle):
        if os.path.exists(bundle):
            filters = self.api.get_filters()

            def filtering(file):
                if file in filters.config_files:
                    return True
                if '.{}'.format(file.split('.')[-1]) in filters.extensions:
                    return True
                return False

            def progress_iterator(it):
                return self._progress_bar('hashing files', it)

            files = util.hash_files(bundle, MAX_FILE_SIZE, filtering=filtering, progress_iterator=progress_iterator)
            bundle_obj = Bundle(files, bundle_root_path=bundle)
            return self._create_bundle_from_files(bundle_obj)
        else:
            owner, repo, commit = self._repo_from_repo_string(bundle)
            if owner is None:
                raise DCAnalysisError('"{}" is neither an existing directory, '
                                      'nor a valid repo representation'.format(bundle))
            return self._create_bundle_from_repo(owner, repo, commit)

    def _create_bundle_from_files(self, bundle_obj):
        try:
            res = self.api.create_bundle_from_files(bundle_obj)
            if len(res.missing_files) == 0:
                return res.bundle_id

            def handle_missing(missing):
                file_path = os.path.join(bundle_obj.bundle_root_path, missing)
                file_content = util.file_contents_as_string(file_path, MAX_FILE_SIZE)
                if not file_content:
                    return None
                file_hash = bundle_obj.hash_of_path(missing)
                return file_content, file_hash
            file_content_and_hashes = list(filter(lambda e: e, map(handle_missing, res.missing_files)))
            batches = self._create_batches(file_content_and_hashes, bundle_obj)
            if not self.silent:
                print('preparing for upload, need to upload {} '
                      'batches of in total {} missing files'.format(len(batches), len(res.missing_files)))
            self.api.upload_batches(res.upload_url,
                                    batches,
                                    progress_iterator=lambda it: self._progress_bar('uploading files', it))
            return res.bundle_id
        except ApiException as err:
            if isinstance(err, ApiUnauthorizedException):
                raise DCAnalysisError('Unauthorized')
            elif isinstance(err, ApiRequestBodyTooLarge):
                raise DCAnalysisError('Request body too large')
            else:
                raise DCAnalysisError(err)

    @staticmethod
    def _create_batches(file_content_and_hashes, bundle_obj):
        batches = [[]]
        batch_size = 0
        for file_content, file_hash in file_content_and_hashes:
            file_size = util.utf8len(file_content) + util.utf8len(file_hash)
            if batch_size + file_size < MAX_BATCH_CONTENT_SIZE:
                batch_size = batch_size + file_size
            else:
                batch_size = file_size
                if batch_size > MAX_BATCH_CONTENT_SIZE:
                    path = bundle_obj.path_of_hash(file_hash)
                    raise DCAnalysisError('Cannot upload file {}, contents too large'.format(path))
                batches.append([])
            batches[len(batches) - 1].append((file_content, file_hash))
        return batches

    @staticmethod
    def _repo_from_repo_string(repo_string):
        tokens = repo_string.split('/')
        if len(tokens) is 2:
            return tokens[0], tokens[1], None
        elif len(tokens) is 3:
            return tokens[0], tokens[1], tokens[2]
        else:
            return None, None, None

    def _create_bundle_from_repo(self, owner, repo, commit):
        try:
            res = self.api.create_bundle_from_repo(owner, repo, commit)
            return res.bundle_id
        except ApiException as err:
            raise DCAnalysisError(err)


class DCAnalysisError(Exception):
    pass


class Bundle:
    def __init__(self, files_hash_and_path, bundle_root_path):
        self._files_hash_and_path = files_hash_and_path
        self.path_to_hash = {}
        self.hash_to_path = {}
        for file_hash, path in files_hash_and_path:
            self.path_to_hash[path] = file_hash
            self.hash_to_path[file_hash] = path
        self.bundle_root_path = bundle_root_path

    def to_dict(self):
        res = {}
        for file_hash, path in self._files_hash_and_path:
            res[path] = file_hash
        return res

    def hash_of_path(self, path):
        return self.path_to_hash[path]

    def path_of_hash(self, file_hash):
        return self.hash_to_path.get(file_hash, '?')


class DCAnalysisCLIPrinter:
    def __init__(self, config):
        self.dc_analysis = DCAnalysis(config, silent=False)

    def login(self):
        try:
            res = self.dc_analysis.login()
            if res != 'private' and res != 'public':
                print('opening web browser for user login')
                webbrowser.get().open_new(res)
                print('waiting for login')
                res = self.dc_analysis.wait_for_login().type
            if res == 'private':
                print('login as private user successful')
            elif res == 'public':
                print('login as public user successful')
                print('')
                print(PUBLIC_NOTICE)
                print('')
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    def logout(self):
        try:
            self.dc_analysis.logout()
            print('logged out')
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    def analyze(self, bundle):
        try:
            res = self.dc_analysis.analyze(bundle)
            self._print_suggestions(res.suggestions, res.url)
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    def diff(self, bundle1, bundle2):
        try:
            res = self.dc_analysis.diff(bundle1, bundle2)
            self._print_suggestions(res.suggestions, res.url)
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    @staticmethod
    def _print_error_and_exit(error):
        print('Error: {}'.format(error))
        exit(1)

    @staticmethod
    def _print_suggestions(suggestions, url):
        count = {
            1: 0,
            2: 0,
            3: 0
        }
        switcher = {
            1: "INFO",
            2: "WARN",
            3: "CRITICAL",
        }
        for file_path, file_ in suggestions['files'].items():
            has_warning_or_critical = False
            for sug_id, positions in file_.items():
                sugg = suggestions['suggestions'][sug_id]
                if sugg['severity'] > 1:
                    has_warning_or_critical = True
            if not has_warning_or_critical:
                continue
            print('file: {}'.format(file_path))
            for sug_id, positions in file_.items():
                sugg = suggestions['suggestions'][sug_id]
                if sugg['severity'] is 1:
                    continue
                msg = sugg['message'].rstrip()
                if msg == '':
                    msg = '<no message>'
                print('  ({}) {}'.format(switcher.get(sugg['severity']), msg))
                print('  positions:')
                for pos in positions:
                    print('    rows: {}-{}, cols: {}-{}'.format(pos['rows'][0],pos['rows'][1],pos['cols'][0],pos['cols'][1]))
            print('')
        for sugg_id, suggestion in suggestions['suggestions'].items():
            count[suggestion['severity']] = count[suggestion['severity']] + 1
        print('DeepCode found {} critical, {} warning and {} info suggestions.'.format(count[3], count[2], count[1]))
        print('View the suggestions in DeepCode: {}'.format(url))


class DCAnalysisJsonPrinter:
    def __init__(self, config):
        self.dc_analysis = DCAnalysis(config, silent=True)

    def login(self):
        try:
            res = self.dc_analysis.login()
            res_dict = {}
            if res == 'public':
                res_dict['publicNoticeMD'] = PUBLIC_NOTICE
            if res == 'private' or res == 'public':
                res_dict['userType'] = res
                res_dict['loggedIn'] = True
            else:
                res_dict['loginURL'] = res
                res_dict['loggedIn'] = False
            print(json.dumps(res_dict))
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    def logout(self):
        try:
            self.dc_analysis.logout()
        except DCAnalysisError as err:
            self._print_error_and_exit(err)

    def wait_for_login(self):
        try:
            res = self.dc_analysis.wait_for_login()
            res_dict = {}
            if res == 'public':
                res_dict['publicNoticeMd'] = PUBLIC_NOTICE
            res_dict['userType'] = res
            res_dict['loggedIn'] = True
        except DCAnalysisError as err:
            self._print_error_and_exit(err)
        res = False
        try:
            res = self.dc_analysis.login()
        except DCAnalysisError as err:
            self._print_error_and_exit(err)
        if not res:
            exit(1)

    def analyze(self, bundle):
        res = {}
        try:
            res = self.dc_analysis.analyze(bundle)
        except DCAnalysisError as err:
            self._print_error_and_exit(err)
        self._print_suggestions(res.suggestions, res.url)

    def diff(self, bundle1, bundle2):
        res = {}
        try:
            res = self.dc_analysis.diff(bundle1, bundle2)
        except DCAnalysisError as err:
            self._print_error_and_exit(err)
        self._print_suggestions(res.suggestions, res.url)

    @staticmethod
    def _print_error_and_exit(error):
        res_dict = {'error': str(error)}
        print(json.dumps(res_dict))
        exit(1)

    @staticmethod
    def _print_suggestions(suggestions, url):
        res = {
            'suggestions': suggestions,
            'url': url
        }
        print(json.dumps(res))
