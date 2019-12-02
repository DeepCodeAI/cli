LOGIN_RESPONSE_FIELDS = ('sessionToken', 'loginURL')
BUNDLE_RESPONSE_FIELDS = ('bundleId', 'uploadURL', 'missingFiles')
ANALYSIS_RESPONSE_FIELDS = (
    'status', 'progress', 'analysisURL', 'analysisResults')
ANALYSIS_RESULTS_FIELDS = ('files', 'suggestions')


BACKEND_STATUS_CODES = {
    'success': 200,
    'login_in_progress': 304,
    'token': 401,
    'invalid_content': 400,
    'invalid_bundle_access': 403,
    'expired_bundle': 404,
    'large_payload': 413
}

ANALYSIS_RESPONSE_STATUSES = {
    'done': 'DONE',
    'dc_done': 'DC_DONE',
    'analyzing': 'ANALYZING',
    'fetching': 'FETCHING',
    'failed': 'FAILED'
}

MAX_POLLS_LIMIT = 1000
POLLING_INTERVAL = 1  # 1sec
