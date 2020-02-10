import time
import json
import asyncio
from operator import itemgetter
from deepcode.src.modules.bundler import DeepCodeBundler
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES, SEVERITIES
from deepcode.src.utils.analysis_utils import construct_issues_complex_txt_view, construct_issues_json_view
from deepcode.src.utils.api_utils import validate_analysis_response
from deepcode.src.utils.cli_utils import construct_progress
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.constants.backend_constants \
    import MAX_POLLS_LIMIT, POLLING_INTERVAL, ANALYSIS_RESPONSE_STATUSES
from deepcode.src.modules.errors_handler import DeepCodeErrorHandler
from deepcode.src.helpers.cli_helpers import ANALYSIS_HELPERS


class DeepCodeAnalyzer:
    def __init__(self, http):
        self.http = http
        self.bundler = DeepCodeBundler(self.http)

    # methods for remote analysis of git repos
    def analyze_repo(self, bundle_path, show_progressbar=True):
        remote_bundle = self.bundler.create_repo_bundle(bundle_path)
        bundle_id = remote_bundle['bundleId']
        return self.analyze(bundle_id, show_progressbar=show_progressbar)

    def analyze_diff_repos(self, bundles=[], show_progressbar=True):
        remote_bundles_ids = []
        for path in bundles:
            r_bundle = self.bundler.create_repo_bundle(path)
            remote_bundles_ids.append(r_bundle['bundleId'])
        bundle_id = '{}/{}'.format(*remote_bundles_ids)
        return self.analyze(bundle_id, show_progressbar=show_progressbar)

    # analyze methods for files bundles
    def analyze_files_bundle(self, bundle_path, show_progressbar=True):
        remote_bundle = self.bundler.create_files_bundle(
            bundle_path, show_progressbar=show_progressbar)
        return self.analyze(remote_bundle['bundleId'], show_progressbar=show_progressbar)

    def diff_analyze_files_bundles(self, paths, show_progressbar=True):
        remote_bundles_ids = []
        loop = asyncio.get_event_loop()

        def _task_func(path):
            remote_bundle_data = self.bundler.create_files_bundle(
                path, show_progressbar=show_progressbar)
            return remote_bundle_data['bundleId']

        async def _tasks(paths):
            for path in paths:
                remote_bundles_ids.append(await loop.run_in_executor(
                    None, _task_func, path))

        loop.run_until_complete(_tasks(paths))
        loop.close()
        bundle_id = '{}/{}'.format(*remote_bundles_ids)
        return self.analyze(bundle_id, show_progressbar=show_progressbar)

    # analyze reused method
    def analyze(self, bundle_id, show_progressbar=True):
        route = DEEPCODE_API_ROUTES['analysis'](bundle_id)
        if show_progressbar:
            with construct_progress(prefix=ANALYSIS_HELPERS['analyzing']) as progress:
                return self.fetch_analysis_from_server(route, bundle_id, progress_bar=progress)
        else:
            return self.fetch_analysis_from_server(route, bundle_id)

    # fetching analysis method
    @DeepCodeErrorHandler.backend_error_decorator
    def fetch_analysis_from_server(self, route, bundle_id, progress_bar=None,):
        # deepcode ignore replace~range~list: using iterator inside forloop is good
        for _ in range(MAX_POLLS_LIMIT):
            # print('before http get fetch_analysis_from_server to route --> ', route)
            analysis_response = self.http.get(route, response_to_json=False)
            analysis_results = analysis_response.json()
            if not validate_analysis_response(analysis_results):
                DeepCodeErrorHandler.raise_backend_error(
                    'invalid_analysis_response',
                    err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                        route, bundle_id, 'invalid_analysis_response'
                    ))
            if progress_bar:
                progress_bar.update(
                    int(analysis_results['progress']*MAX_PROGRESS_VALUE))
            if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['failed']:
                DeepCodeErrorHandler.raise_backend_error('analysis_failed',
                                                         err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                                                             route, bundle_id, 'analysis_failed'
                                                         ))
            if analysis_results['status'] == ANALYSIS_RESPONSE_STATUSES['done']:
                if progress_bar:
                    progress_bar.update(MAX_PROGRESS_VALUE)
                return analysis_results['analysisResults'] if 'analysisResults' in analysis_results else None
            time.sleep(POLLING_INTERVAL)

    # display results methods
    def analysis_results_in_json(self, analysis_results, is_silent=False):
        return construct_issues_json_view(analysis_results, is_silent)

    def display_analysis_results_in_txt(self, analysis_results, is_silent=False):
        return construct_issues_complex_txt_view(analysis_results, is_silent)
