import progressbar
import os
import sys
import time
from deepcode.src.constants.config_constants import MAX_FILE_SIZE, MAX_BATCH_CONTENT_SIZE, CURRENT_FOLDER_PATH
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.utils.analysis_utils\
    import hash_files, file_contents_as_string, extract_data_from_remote_bundle_path, validate_data_for_remote
from deepcode.src.modules.errors_handler import ErrorHandler
from deepcode.src.helpers.cli_helpers import BUNDLE_HELPERS
from deepcode.src.helpers.errors_messages import BACKEND_ERRORS
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES
from deepcode.src.constants.backend_constants \
    import BUNDLE_RESPONSE_FIELDS, MAX_POLLS_LIMIT, POLLING_INTERVAL, ANALYSIS_RESPONSE_STATUSES, BACKEND_STATUS_CODES

from deepcode.src.utils.api_utils import validate_remote_bundle_response


class DeepCodeBundler:
    def __init__(self, http):
        self.http = http
        self.abs_bundle_paths = {}
        self.hashes_bundles = {}
        self.server_bundles = {}

    # remote repo bundles
    def create_repo_bundle(self, bundle_path):
        path_dict_to_remote_bundle = self.handle_remote_path(bundle_path)
        remote_bundle = self.create_server_remote_bundle(
            path_dict_to_remote_bundle)
        return remote_bundle

    @ErrorHandler.backend_error_decorator
    def create_server_remote_bundle(self, path_dict_to_remote_bundle):
        remote_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
            'data': {key: path_dict_to_remote_bundle[key] for key in path_dict_to_remote_bundle if path_dict_to_remote_bundle[key] is not None},
        })
        if not validate_remote_bundle_response(remote_bundle):
            ErrorHandler.raise_backend_error('invalid_bundle_response',
                                             err_details=ErrorHandler.construct_backend_error_for_report(
                                                 DEEPCODE_API_ROUTES['create_bundle'], remote_bundle, 'invalid_bundle_response'))
        return remote_bundle

    @ErrorHandler.bundle_path_error_decorator
    def handle_remote_path(self, bundle_path):
        remote_data = extract_data_from_remote_bundle_path(bundle_path)
        if not validate_data_for_remote(remote_data):
            ErrorHandler.raise_path_error('invalid_repo_path')
        return remote_data

    # files bundles
    def create_files_bundle(self, bundle_path, show_progressbar=True):
        # filters
        self.files_filters = self.create_files_fiters_from_server()
        # absolute bundle path
        abs_path = self.create_abs_bundle_path(bundle_path)
        self.abs_bundle_paths[abs_path] = abs_path
        # create hashes bundle
        self.create_hashes_bundle(abs_path, show_progressbar=show_progressbar)
        # create hashes remote bundle
        if not self.hashes_bundles[abs_path] or not len(self.hashes_bundles[abs_path]):
            ErrorHandler.raise_path_error('no_path')
        self.server_bundles[abs_path] = self.create_files_server_bundle(
            abs_path)
        # check for missing files and upload missing files
        self.handle_server_bundle_missing_files(
            abs_path, show_progressbar=show_progressbar)
        return self.server_bundles[abs_path]

    @ErrorHandler.backend_error_decorator
    def create_files_fiters_from_server(self):
        return self.http.get(DEEPCODE_API_ROUTES['files_filters'])

    @ErrorHandler.bundle_path_error_decorator
    def create_abs_bundle_path(self, bundle_path):
        is_current_path = bundle_path is CURRENT_FOLDER_PATH
        result_path = os.path.abspath(
            bundle_path) if is_current_path else bundle_path
        result_path = os.path.join(os.path.sep, result_path)
        if not os.path.exists(result_path):
            ErrorHandler.raise_path_error('no_path')
        return result_path

    @ErrorHandler.files_bundle_error_decorator
    def create_hashes_bundle(self, bundle_path, show_progressbar=True):
        self.hashes_bundles[bundle_path] = hash_files(
            self.abs_bundle_paths[bundle_path],
            MAX_FILE_SIZE,
            self.files_filters,
            show_progressbar=show_progressbar,
            progress_iterator=lambda iterator, max_value: progressbar.progressbar(
                iterator, max_value=max_value, prefix=BUNDLE_HELPERS['creating'](bundle_path))

        )

    @ErrorHandler.backend_error_decorator
    def create_files_server_bundle(self, bundle_path):
        server_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
            'data': {'files': self.hashes_bundles[bundle_path]}})
        if not validate_remote_bundle_response(server_bundle):
            ErrorHandler.raise_backend_error('invalid_bundle_response',
                                             err_details=ErrorHandler.construct_backend_error_for_report(
                                                 DEEPCODE_API_ROUTES['create_bundle'], server_bundle, 'invalid_bundle_response'))
        return server_bundle

    @ErrorHandler.backend_error_decorator
    def handle_server_bundle_missing_files(self, bundle_path, show_progressbar=True):
        def _iterate_func(progress_bar=None):
            bundle_to_check = self.server_bundles[bundle_path]
            for idx in range(MAX_PROGRESS_VALUE):
                if progress_bar:
                    progress_bar.update(idx)
                bundle_to_check = self.http.get(
                    DEEPCODE_API_ROUTES['check_bundle'](bundle_to_check['bundleId']))

                missing_files_exist = self.missing_files_in_server_bundle(
                    bundle_to_check)
                if not missing_files_exist:
                    if progress_bar:
                        progress_bar.update(MAX_PROGRESS_VALUE)
                    break
                self.upload_missing_files(bundle_to_check, bundle_path)
            self.server_bundles[bundle_path] = bundle_to_check

        if show_progressbar:
            with progressbar.ProgressBar(max_value=MAX_PROGRESS_VALUE, min_value=0, prefix=BUNDLE_HELPERS['uploading'](bundle_path)) as progress:
                return _iterate_func(progress_bar=progress)
        else:
            return _iterate_func()

    def missing_files_in_server_bundle(self, bundle):
        *_, missingFiles = BUNDLE_RESPONSE_FIELDS
        return missingFiles in bundle and len(bundle[missingFiles])

    @ErrorHandler.backend_error_decorator
    def upload_missing_files(self, server_bundle, bundle_path):

        def _upload_missing_to_server(batch):
            bundle_id = server_bundle['bundleId']
            return self.http.post(DEEPCODE_API_ROUTES['upload_files'](bundle_id), {
                'data': batch,
                'charset': True
            }, response_to_json=False)

        missing_files_batch = self.create_missing_files_batch(
            server_bundle['missingFiles'], self.hashes_bundles[bundle_path], self.abs_bundle_paths[bundle_path])
        response = _upload_missing_to_server(missing_files_batch)
        # handle too big payload of missing files
        if response.status_code == BACKEND_STATUS_CODES['large_payload']:
            separate_batches = self.split_missing_files_into_batches(
                missing_files_batch)
            for idx in separate_batches:
                _upload_missing_to_server(separate_batches[idx])
                time.sleep(POLLING_INTERVAL)  # delay between uplading batches

    @ErrorHandler.files_bundle_error_decorator
    def create_missing_files_batch(self, missing_files, hashes_bundle, abs_bundle_path):
        missing_files_batch = []
        for file_path in missing_files:
            p = file_path[1:] if file_path[0] == '/' else file_path
            file_hash = hashes_bundle[p]
            file_content = file_contents_as_string(
                os.path.join(abs_bundle_path, p))
            if file_content is not None:
                missing_files_batch.append(
                    {'fileHash': file_hash, 'fileContent': file_content})
        return missing_files_batch

    def split_missing_files_into_batches(self, missing_files_batch):
        if missing_files_batch > MAX_BATCH_CONTENT_SIZE:
            separate_batches = []
            single_batch = []
            for idx in missing_files_batch:
                single_batch.append(missing_files_batch[idx])
                if sys.getsizeof(single_batch) == MAX_BATCH_CONTENT_SIZE:
                    separate_batches.append(single_batch)
                    single_batch = []
            return separate_batches
        return missing_files_batch
