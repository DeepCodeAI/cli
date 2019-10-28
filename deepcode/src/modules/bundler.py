import progressbar
import os
import sys
import time
from deepcode.src.constants.config_constants import MAX_FILE_SIZE, MAX_BATCH_CONTENT_SIZE, CURRENT_FOLDER_PATH
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.utils.analysis_utils\
    import hash_files, file_contents_as_string, extract_data_from_remote_bundle_path, validate_data_for_remote
from deepcode.src.modules.errors_handler import DeepCodeErrors
from deepcode.src.helpers.cli_helpers import BUNDLE_HELPERS
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES
from deepcode.src.constants.backend_constants \
    import BUNDLE_RESPONSE_FIELDS, MAX_POLLS_LIMIT, POLLING_INTERVAL, ANALYSIS_RESPONSE_STATUSES, BACKEND_STATUS_CODES

from deepcode.src.utils.api_utils import validate_remote_bundle_response


class DeepCodeBundler:
    def __init__(self, http):
        self.http = http
        self.abs_bundle_path = ''
        self.hashes_bundle = None
        self.server_bundle = None
        self.server_filters = None

    @DeepCodeErrors.backend_error_decorator
    def create_repo_remote_bundle(self, bundle_path):
        remote_bundle_data = self.handle_remote_path(bundle_path)
        remote_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
            'data': {key: remote_bundle_data[key] for key in remote_bundle_data if remote_bundle_data[key] is not None},
        })
        if not validate_remote_bundle_response(remote_bundle):
            DeepCodeErrors.raise_backend_error('invalid_bundle_response')
        return remote_bundle

    @DeepCodeErrors.bundle_path_error_decorator
    def handle_remote_path(self, bundle_path):
        remote_data = extract_data_from_remote_bundle_path(bundle_path)
        if not validate_data_for_remote(remote_data):
            DeepCodeErrors.raise_path_error('invalid_repo_path')
        return remote_data

    @DeepCodeErrors.backend_error_decorator
    def create_files_remote_bundle(self, bundle_path):
        self.create_abs_bundle_path(bundle_path)
        # get files filters
        self.get_server_filters_files()
        # create hashes bundle
        self.create_hashes_bundle()
        # create hashes remote bundle
        if not self.hashes_bundle or not len(self.hashes_bundle):
            return None, self.abs_bundle_path
        self.server_bundle = self.create_files_server_bundle()
        # check for missing files and upload missing files
        self.handle_server_bundle_missing_files()
        return (self.server_bundle, self.abs_bundle_path)

    @DeepCodeErrors.backend_error_decorator
    def get_server_filters_files(self):
        self.files_filters = self.http.get(
            DEEPCODE_API_ROUTES['files_filters'])

    @DeepCodeErrors.bundle_path_error_decorator
    def create_abs_bundle_path(self, bundle_path):
        is_current_path = bundle_path is CURRENT_FOLDER_PATH
        self.abs_bundle_path = os.path.abspath(
            bundle_path) if is_current_path else bundle_path
        if not os.path.exists(self.abs_bundle_path):
            DeepCodeErrors.raise_path_error('no_path')

    @DeepCodeErrors.files_bundle_error_decorator
    def create_hashes_bundle(self):
        self.hashes_bundle = hash_files(
            self.abs_bundle_path,
            MAX_FILE_SIZE,
            self.files_filters,
            progress_iterator=lambda iterator, max_value: progressbar.progressbar(
                iterator, max_value=max_value, prefix=BUNDLE_HELPERS['creating'])
        )

    @DeepCodeErrors.bundle_path_error_decorator
    def create_files_server_bundle(self):
        server_bundle = self.http.post(DEEPCODE_API_ROUTES['create_bundle'], {
            'data': {'files': self.hashes_bundle}})
        if not validate_remote_bundle_response(server_bundle):
            DeepCodeErrors.raise_backend_error('invalid_bundle_response')
        return server_bundle

    @DeepCodeErrors.backend_error_decorator
    def handle_server_bundle_missing_files(self):
        bundle_to_check = self.server_bundle
        with progressbar.ProgressBar(max_value=MAX_PROGRESS_VALUE, min_value=0, prefix=BUNDLE_HELPERS['uploading']) as progress:

            for idx in range(MAX_PROGRESS_VALUE):
                progress.update(idx)
                bundle_to_check = self.http.get(
                    DEEPCODE_API_ROUTES['check_bundle'](bundle_to_check['bundleId']))

                missing_files_exist = self.missing_files_in_server_bundle(
                    bundle_to_check)
                if not missing_files_exist:
                    progress.update(MAX_PROGRESS_VALUE)
                    break
                self.upload_missing_files(bundle_to_check)
            return bundle_to_check

    def missing_files_in_server_bundle(self, bundle):
        *_, missingFiles = BUNDLE_RESPONSE_FIELDS
        return missingFiles in bundle and len(bundle[missingFiles])

    @DeepCodeErrors.backend_error_decorator
    def upload_missing_files(self, server_bundle):

        def _upload_missing_to_server(batch):
            bundle_id = self.server_bundle['bundleId']
            return self.http.post(DEEPCODE_API_ROUTES['upload_files'](bundle_id), {
                'data': batch,
                'charset': True
            }, response_to_json=False)

        missing_files_batch = self.create_missing_files_batch(
            server_bundle['missingFiles'], self.hashes_bundle, self.abs_bundle_path)
        response = _upload_missing_to_server(missing_files_batch)
        # handle too big payload of missing files
        if response.status_code == BACKEND_STATUS_CODES['large_payload']:
            separate_batches = self.split_missing_files_into_batches(
                missing_files_batch)
            for idx in separate_batches:
                _upload_missing_to_server(separate_batches[idx])
                time.sleep(POLLING_INTERVAL)  # delay between uplading batches

    @DeepCodeErrors.files_bundle_error_decorator
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
