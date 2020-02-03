import os
import sys
import time
import asyncio
from progressbar import progressbar
from deepcode.src.modules.errors_handler import DeepCodeErrorHandler

from deepcode.src.utils.analysis_utils\
    import hash_files, file_contents_as_string, extract_data_from_remote_bundle_path, validate_data_for_remote
from deepcode.src.utils.api_utils import validate_remote_bundle_response
from deepcode.src.utils.cli_utils import construct_progress, progress_iterator

from deepcode.src.constants.config_constants import MAX_REQUEST_BODY_SIZE, DEEPCODE_API_ROUTES
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.constants.backend_constants \
    import BUNDLE_RESPONSE_FIELDS, POLLING_INTERVAL, BACKEND_STATUS_CODES
from deepcode.src.helpers.cli_helpers import BUNDLE_HELPERS


class DeepCodeBundler:
    def __init__(self, http):
        self.http = http
        self.abs_bundle_paths = {}
        self.hashes_bundles = {}
        self.server_bundles = {}

    # remote repo bundles
    def create_repo_bundle(self, bundle_path):
        path_dict = self.handle_remote_path(bundle_path)
        return self.create_server_remote_bundle(path_dict)

    @DeepCodeErrorHandler.backend_error_decorator
    def create_server_remote_bundle(self, path_dict_to_remote_bundle):
        data = {
            key: path_dict_to_remote_bundle[key]
            for key in path_dict_to_remote_bundle 
            if path_dict_to_remote_bundle[key] is not None
            }
        # print('create_server_remote_bundle http post with data --> ', data)
        remote_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {'data': data})
        if not validate_remote_bundle_response(remote_bundle):
            DeepCodeErrorHandler.raise_backend_error('invalid_bundle_response',
                                                     err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                                                         DEEPCODE_API_ROUTES['create_bundle'], remote_bundle, 'invalid_bundle_response'))
        return remote_bundle

    @DeepCodeErrorHandler.bundle_path_error_decorator
    def handle_remote_path(self, bundle_path):
        remote_data = extract_data_from_remote_bundle_path(bundle_path)
        if not validate_data_for_remote(remote_data):
            DeepCodeErrorHandler.raise_path_error('invalid_repo_path')
        return remote_data

    # files bundles
    def create_files_bundle(self, bundle_path, show_progressbar=True):
        # filters
        self.files_filters = self.create_files_filters_from_server()
        # absolute bundle path
        abs_path = self.create_abs_bundle_path(bundle_path)
        self.abs_bundle_paths[abs_path] = abs_path
        # create hashes bundle
        self.hashes_bundles[abs_path] = self.create_hashes_bundle(
            abs_path, show_progressbar=show_progressbar)
        # print('hashes_bundles --> ', self.hashes_bundles)
        # create remote bundle on server
        server_start_bundle = self.create_files_server_bundle(
            self.hashes_bundles[abs_path])
        # print('server_start_bundle --> ', server_start_bundle)
        # check for missing files and upload missing files
        self.server_bundles[abs_path] = self.handle_server_bundle_missing_files(
            server_start_bundle,
            self.hashes_bundles[abs_path],
            show_progressbar=show_progressbar)
        # print('server_bundles --> ', self.server_bundles)
        return self.server_bundles[abs_path]

    @DeepCodeErrorHandler.backend_error_decorator
    def create_files_filters_from_server(self):
        res = self.http.get(DEEPCODE_API_ROUTES['files_filters'])
        return res

    @DeepCodeErrorHandler.bundle_path_error_decorator
    def create_abs_bundle_path(self, bundle_path):
        result_path = os.path.join(os.path.sep, os.path.realpath(bundle_path))
        if not os.path.exists(result_path):
            DeepCodeErrorHandler.raise_path_error('no_path')
        return result_path

    @DeepCodeErrorHandler.files_bundle_error_decorator
    def create_hashes_bundle(self, bundle_path, show_progressbar=True):
        hashes_bundle = hash_files(
            self.abs_bundle_paths[bundle_path],
            MAX_REQUEST_BODY_SIZE,
            self.files_filters,
            show_progressbar=show_progressbar,
            progress_iterator=progress_iterator(
                prefix=BUNDLE_HELPERS['creating'])
        )
        if not len(hashes_bundle):
            DeepCodeErrorHandler.raise_files_bundle_error('empty_bundle')
        return hashes_bundle

    @DeepCodeErrorHandler.backend_error_decorator
    def create_files_server_bundle(self, hashes_bundle):
        # print('create_files_server_bundle. hashes_bundle --> ', hashes_bundle)
        server_bundle = self.http.post(
            DEEPCODE_API_ROUTES['create_bundle'], 
            {'data': {'files': hashes_bundle}}
            )
        if not validate_remote_bundle_response(server_bundle):
            DeepCodeErrorHandler.raise_backend_error('invalid_bundle_response',
                                                     err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                                                         DEEPCODE_API_ROUTES['create_bundle'], server_bundle, 'invalid_bundle_response'))
        return server_bundle

    @DeepCodeErrorHandler.backend_error_decorator
    def check_server_bundle_on_server(self, bundle_id):
        return self.http.get(DEEPCODE_API_ROUTES['check_bundle'](bundle_id))

    @DeepCodeErrorHandler.backend_error_decorator
    def handle_server_bundle_missing_files(self, server_bundle, hashes_bundle, show_progressbar=True):
        def _iterate_func(progress_bar=None):
            bundle_to_check = server_bundle
            # deepcode ignore replace~range~list: Iterator in for-loop is considered good
            for idx in range(MAX_PROGRESS_VALUE):
                if progress_bar:
                    progress_bar.update(idx)
                missing_files_exist = self.missing_files_in_server_bundle(
                    bundle_to_check)
                if not missing_files_exist:
                    if progress_bar:
                        progress_bar.update(MAX_PROGRESS_VALUE)
                    break
                self.upload_missing_files(bundle_to_check, hashes_bundle, show_progressbar)
                bundle_to_check = self.check_server_bundle_on_server(
                    bundle_to_check['bundleId'])
            return bundle_to_check

        if show_progressbar:
            with construct_progress(prefix=BUNDLE_HELPERS['uploading']) as progress:
                return _iterate_func(progress_bar=progress)
        else:
            return _iterate_func()

    def missing_files_in_server_bundle(self, bundle):
        *_, missingFiles = BUNDLE_RESPONSE_FIELDS
        return missingFiles in bundle and len(bundle[missingFiles])

    @DeepCodeErrorHandler.backend_error_decorator
    def upload_missing_files(self, server_bundle, hashes_bundle, show_progressbar):
        # print('!!! started upload_missing_files !!!')
        def _upload_missing_to_server(batch):
            bundle_id = server_bundle['bundleId']
            return self.http.post(DEEPCODE_API_ROUTES['upload_files'](bundle_id), {
                'data': batch,
                'charset': True
            }, response_to_json=False)

        missing_files_batch = self.create_missing_files_batch(
            server_bundle['missingFiles'], hashes_bundle)
        # split into smaller batches if necessary
        separate_batches = self.split_missing_files_into_batches(
            missing_files_batch)
        i = 1

        multi_bundle_progress_bar = None
        if show_progressbar:
            multi_bundle_progress_bar = construct_progress(prefix=BUNDLE_HELPERS['uploading'], min_value=0, max_value=len(separate_batches))


        for batch in separate_batches:
            if multi_bundle_progress_bar is None:
                multi_bundle_progress_bar.update(i)
            i = i + 1
            _upload_missing_to_server(batch)
            time.sleep(POLLING_INTERVAL)  # delay between uplading batches

    def compute_files_batch_size(self, batch):
        return len(batch['fileHash']) + len(batch['fileContent']) + 20   # TODO what is the exact size? guess 20 or fewer extra bytes for formatting
                                                                         # TODO check: are encoding risks handled properly?
    def compute_files_batch_list_size(self, batch):
        # Process batch as created by create_missing_files_batch(). Previous versions
        # computed size using sys.getsizeof(), but this results in a "shallow" computation
        # excluding the actual data objects
        total_size = 0
        for f in batch:
            total_size += self.compute_files_batch_size(f)
        return total_size

    @DeepCodeErrorHandler.files_bundle_error_decorator
    def create_missing_files_batch(self, missing_files, hashes_bundle):
        missing_files_batch = []
        for file_path in missing_files:
            # p = file_path[1:] if file_path[0] == '/' else file_path
            p = file_path
            file_hash = hashes_bundle[p]
            file_content = file_contents_as_string(p)
            if file_content is not None:
                missing_files_batch.append(
                    {'fileHash': file_hash, 'fileContent': file_content})
        return missing_files_batch



    @DeepCodeErrorHandler.files_bundle_error_decorator
    def split_missing_files_into_batches(self, missing_files_batch):
        if self.compute_files_batch_list_size(missing_files_batch) > MAX_REQUEST_BODY_SIZE:
            separate_batches = []
            single_batch = []
            for batch in missing_files_batch:
                if self.compute_files_batch_list_size(single_batch) + self.compute_files_batch_size(batch) >= MAX_REQUEST_BODY_SIZE:
                    separate_batches.append(single_batch)
                    single_batch = []
                single_batch.append(batch)
            return separate_batches
        return missing_files_batch
