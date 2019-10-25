import os
import time
import json
import progressbar
from operator import itemgetter
from deepcode.src.modules.bundler import DeepCodeBundler
from deepcode.src.constants.config_constants \
    import DEEPCODE_API_ROUTES, DEEPCODE_CONFIG_NAMES, CURRENT_FOLDER_PATH, MAX_BATCH_CONTENT_SIZE, MAX_FILE_SIZE, SEVERITIES
from deepcode.src.utils.analysis_utils\
    import hash_files, utf8len, \
    file_contents_as_string, \
    extract_data_from_remote_bundle_path, \
    validate_data_for_remote, pass_filter, \
    construct_issue_positions_txt_view, \
    construct_issue_txt_view
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.constants.backend_constants import BUNDLE_RESPONSE_FIELDS


class DeepCodeAnalyzer:
    def __init__(self, http):
        self.bundler = DeepCodeBundler()
        self.http = http
        self.current_bundle_id = ''
        self.abs_bundle_path = ''

    # remote analysis for git repos
    def analyze_repo(self, bundle_path):
        remote_data = extract_data_from_remote_bundle_path(bundle_path)
        if not validate_data_for_remote(remote_data):
            print('Not valid remote bundle path')
            return
        remote_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
            'data': {key: remote_data[key] for key in remote_data if remote_data[key] is not None},
        })
        self.current_bundle_id = remote_bundle['bundleId']
        analysis_results = self.get_analysis_from_server()
        # TODO: validate response
        return analysis_results

    def handle_bundle_path(self, bundle_path):
        is_current_path = bundle_path is CURRENT_FOLDER_PATH
        self.abs_bundle_path = os.path.abspath(
            bundle_path) if is_current_path else bundle_path
        if not os.path.exists(self.abs_bundle_path):
            raise Exception('not valid path to analyze')

    # TODO: refactor later
    def analyze_files_bundle(self, bundle_path):
        self.handle_bundle_path(bundle_path)

        # TODO: temp diabled while testing
        # # get files filters
        # files_filters = self.http.get(DEEPCODE_API_ROUTES['files_filters'])
        # print('Creating bundle...')
        # hashes_bundle = self.bundler.create_hashes_bundle(
        #     self.abs_bundle_path, files_filters)

        # server_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
        #     'data': {'files': hashes_bundle}})
        # self.current_bundle_id = server_bundle['bundleId']
        # print('Analyzing...')
        # self.handle_server_bundle_missing_files(server_bundle, hashes_bundle, self.abs_bundle_path)
        # analysis_results = self.get_analysis_from_server()
        # return analysis_results
        return True

    def handle_server_bundle_missing_files(self, server_bundle, hashes_bundle):
        MAX_POLLS_LIMIT = 1000
        POLLING_INTERVAL = 1  # 1sec
        bundle_to_check = server_bundle
        for _ in range(MAX_POLLS_LIMIT):
            missing_files_exist = self.missing_files_in_server_bundle(
                bundle_to_check)
            if missing_files_exist:
                self.upload_missing_files(bundle_to_check, hashes_bundle)
                # check bundle on server
                bundle_to_check = self.http.get(
                    DEEPCODE_API_ROUTES['check_bundle'](self.current_bundle_id))
                time.sleep(POLLING_INTERVAL)
                continue
            break

    def missing_files_in_server_bundle(self, bundle):
        *_, missingFiles = BUNDLE_RESPONSE_FIELDS
        return missingFiles in bundle and len(bundle[missingFiles])

    def upload_missing_files(self, server_bundle, hashes_bundle):
        missing_files_batch = self.bundler.create_missing_files_batch(
            server_bundle['missingFiles'], hashes_bundle)
        self.http.post(DEEPCODE_API_ROUTES['upload_files'](self.current_bundle_id), {
            'data': missing_files_batch,
            'charset': True
        }, response_to_json=False)

    def get_analysis_from_server(self):
        MAX_POLLS_LIMIT = 1000
        POLLING_INTERVAL = 1  # 1sec
        analysis_results = {}
        with progressbar.ProgressBar(max_value=MAX_PROGRESS_VALUE, prefix="DeepCode analysis progress: ") as bar:
            for _ in range(MAX_POLLS_LIMIT):
                analysis_response = self.http.get(
                    DEEPCODE_API_ROUTES['analysis'](self.current_bundle_id), response_to_json=False)
                print(analysis_response.content)
                analysis_results = analysis_response.json()
                bar.update(
                    int(analysis_results['progress']*MAX_PROGRESS_VALUE))
                if analysis_results['status'] == 'DONE':
                    bar.update(MAX_PROGRESS_VALUE)
                    return analysis_results['analysisResults']
                time.sleep(POLLING_INTERVAL)

    def analysis_results_in_json(self, analysis_results):
        with open(os.path.join(os.path.expanduser('~'), 'mockedjson.json')) as mocked:
            return json.load(mocked)
        # return json.dumps(analysis_results)

    def display_analysis_results_in_txt(self, analysis_results):
        result_txt = ''
        print('BUNDLE', self.abs_bundle_path)
        with open(os.path.join(os.path.expanduser('~'), 'mockedjson.json')) as mocked:
            analysis_results = json.load(mocked)

        files, suggestions = itemgetter(
            'files', 'suggestions')(analysis_results)
        files_list_last_element_idx = len(files)-1
        for file_index, file_path in enumerate(files):
            issue_file_path = os.path.join(self.abs_bundle_path, file_path[1:])
            for suggestion in files[file_path]:
                issues_positions_list = files[file_path][suggestion]
                issue_severity_number = suggestions[suggestion]['severity']
                issue_message = suggestions[suggestion]['message']
                issue_txt_view = construct_issue_txt_view(
                    issue_file_path,
                    issues_positions_list,
                    issue_severity_number,
                    issue_message
                )
                result_txt += \
                    issue_txt_view \
                    if file_index == files_list_last_element_idx \
                    else '{}\n'.format(issue_txt_view)

        return result_txt
