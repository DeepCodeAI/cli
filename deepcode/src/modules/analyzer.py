import os
import sys
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
    construct_issue_txt_view, \
    execute_tasks_threads
from deepcode.src.utils.api_utils import validate_remote_bundle_response, validate_analysis_response
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.constants.backend_constants \
    import BUNDLE_RESPONSE_FIELDS, MAX_POLLS_LIMIT, POLLING_INTERVAL, ANALYSIS_RESPONSE_STATUSES, BACKEND_STATUS_CODES
from deepcode.src.helpers.errors_messages import BACKEND_ERRORS
from deepcode.src.modules.errors_handler import DeepCodeErrors
from deepcode.src.helpers.cli_helpers import BUNDLE_HELPERS, ANALYSIS_HELPERS


class DeepCodeAnalyzer:
    def __init__(self, http):
        self.http = http
        self.bundler = DeepCodeBundler(self.http)

    def _err_in_result(self, result_dict):
        return 'error' in result_dict

    # methods for remote analysis of git repos
    @DeepCodeErrors.backend_error_decorator
    def analyze_repo(self, bundle_path, is_cli_mode=True):
        remote_bundle = self.bundler.create_repo_remote_bundle(bundle_path)
        if self._err_in_result(remote_bundle):
            return remote_bundle
        bundle_id = remote_bundle['bundleId']
        return self.analyze(bundle_id, is_progressbar=is_cli_mode)

    @DeepCodeErrors.backend_error_decorator
    def analyze_diff_repos(self, bundles=[], is_cli_mode=True):
        remote_bundles_ids = []
        for path in bundles:
            r_bundle = self.bundler.create_repo_remote_bundle(path)
            if self._err_in_result(r_bundle):
                return r_bundle
            remote_bundles_ids.append(r_bundle['bundleId'])
        bundle_id = '{}/{}'.format(*remote_bundles_ids)
        return self.analyze(bundle_id, is_progressbar=is_cli_mode)

    # analyze methods for files bundles
    @DeepCodeErrors.backend_error_decorator
    def analyze_files_bundle(self, bundle_path, is_cli_mode=True):
        self.bundler.create_files_fiters_from_server()
        remote_bundle = self.bundler.create_files_remote_bundle(
            bundle_path, is_progressbar=is_cli_mode)
        if 'error' in remote_bundle:
            return remote_bundle
        return self.analyze(remote_bundle['bundleId'], is_progressbar=is_cli_mode)

    def diff_analyze_files_bundles(self, paths, is_cli_mode=True):
        self.bundler.create_files_fiters_from_server()
        remote_bundles_ids = []
        thread_error = None

        def threads_cb(*p):
            path = ''.join(p)
            remote_bundle_data = self.bundler.create_files_remote_bundle(
                path, is_progressbar=is_cli_mode)
            return remote_bundle_data

        def thread_results_cb(remote_bundle_data):
            if 'error' in remote_bundle_data:
                nonlocal thread_error, remote_bundles_ids
                thread_error = remote_bundle_data
                return
            remote_bundles_ids.append(remote_bundle_data['bundleId'])

        execute_tasks_threads(
            threads_cb=threads_cb,
            thread_result_cb=thread_results_cb,
            target=paths
        )
        if thread_error:
            return thread_error
        else:
            bundle_id = '{}/{}'.format(*remote_bundles_ids)
            return self.analyze(bundle_id, is_progressbar=is_cli_mode)

    # analyze reused method
    @DeepCodeErrors.backend_error_decorator
    def analyze(self, bundle_id, is_progressbar=True):
        route = DEEPCODE_API_ROUTES['analysis'](bundle_id)
        if is_progressbar:
            with progressbar.ProgressBar(max_value=MAX_PROGRESS_VALUE, min_value=0, prefix=ANALYSIS_HELPERS['analyzing']) as progress:
                return self.fetch_analysis_from_server(route, bundle_id, progress_bar=progress)
        else:
            return self.fetch_analysis_from_server(route, bundle_id)

    # fetching analysis method
    def fetch_analysis_from_server(self, route, bundle_id, progress_bar=None,):
        for _ in range(MAX_POLLS_LIMIT):
            analysis_response = self.http.get(route, response_to_json=False)

            analysis_results = analysis_response.json()
            if not validate_analysis_response(analysis_results):
                DeepCodeErrors.raise_backend_error(
                    'invalid_analysis_response',
                    err_details=DeepCodeErrors.construct_backend_error_for_report(
                        route, bundle_id, 'invalid_analysis_response'
                    ))
            if progress_bar:
                progress_bar.update(
                    int(analysis_results['progress']*MAX_PROGRESS_VALUE))
            if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['failed']:
                DeepCodeErrors.raise_backend_error('analysis_failed',
                                                   err_details=DeepCodeErrors.construct_backend_error_for_report(
                                                       route, bundle_id, 'analysis_failed'
                                                   ))

            if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['done']:
                if progress_bar:
                    progress_bar.update(MAX_PROGRESS_VALUE)
                return analysis_results['analysisResults'] if 'analysisResults' in analysis_results else None
            time.sleep(POLLING_INTERVAL)

    # display results methods
    def analysis_results_in_json(self, analysis_results):
        return json.dumps(analysis_results)

    def display_analysis_results_in_txt(self, analysis_results, is_repo=False):
        result_txt = ''
        files, suggestions = itemgetter(
            'files', 'suggestions')(analysis_results)
        if not len(files) and not len(suggestions):
            return ANALYSIS_HELPERS['empty_results']
        files_list_last_element_idx = len(files)-1
        for file_index, file_path in enumerate(files):
            issue_file_path = file_path
            # issue_file_path = file_path if is_repo else os.path.join(
            #     self.abs_bundle_path, file_path[1:])
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
