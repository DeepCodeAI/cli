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
    construct_issue_txt_view
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
        self.abs_bundle_path = None

    # remote analysis for git repos
    def analyze_repo(self, bundle_path):
        remote_bundle = self.bundler.create_repo_remote_bundle(bundle_path)
        self.abs_bundle_path = bundle_path
        return self.analyze(remote_bundle['bundleId'])

    # analyze files bundles
    @DeepCodeErrors.backend_error_decorator
    def analyze_files_bundle(self, bundle_path):
        remote_bundle, abs_bundle_path = self.bundler.create_files_remote_bundle(
            bundle_path)
        if not remote_bundle:
            return BUNDLE_HELPERS['empty']
        self.abs_bundle_path = abs_bundle_path
        return self.analyze(remote_bundle['bundleId'])

    @DeepCodeErrors.backend_error_decorator
    def analyze(self, bundle_id):
        with progressbar.ProgressBar(max_value=MAX_PROGRESS_VALUE, min_value=0, prefix=ANALYSIS_HELPERS['analyzing']) as progress:
            for _ in range(MAX_POLLS_LIMIT):
                analysis_response = self.http.get(
                    DEEPCODE_API_ROUTES['analysis'](bundle_id), response_to_json=False)

                analysis_results = analysis_response.json()
                if not validate_analysis_response(analysis_results):
                    DeepCodeErrors.raise_backend_error(
                        'invalid_analysis_response')
                progress.update(
                    int(analysis_results['progress']*MAX_PROGRESS_VALUE))
                if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['failed']:
                    DeepCodeErrors.raise_backend_error('analysis_failed', err_details={
                        'route': DEEPCODE_API_ROUTES['analysis'](bundle_id),
                        'error': 'Analysis ended up with status FAILED '
                    })
                if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['done']:
                    progress.update(MAX_PROGRESS_VALUE)
                    return analysis_results['analysisResults'] if 'analysisResults' in analysis_results else None
                time.sleep(POLLING_INTERVAL)

    def analysis_results_in_json(self, analysis_results):
        return json.dumps(analysis_results)

    def display_analysis_results_in_txt(self, analysis_results, is_repo=False):
        result_txt = ''
        files, suggestions = itemgetter(
            'files', 'suggestions')(analysis_results)
        files_list_last_element_idx = len(files)-1
        for file_index, file_path in enumerate(files):
            issue_file_path = file_path if is_repo else os.path.join(
                self.abs_bundle_path, file_path[1:])
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
