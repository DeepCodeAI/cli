DEEPCODE_PACKAGE_NAME = 'deepcode'
DEEPCODE_CONFIG_FILENAME = '.deepcodeConfig'
DEEPCODE_SOURCE_NAME = {'source': 'cli'}
DEEPCODE_BACKEND_HOST = 'https://www.deepcode.ai'
DEEPCODE_API_PREFIX = 'publicapi'
DEEPCODE_API_ROUTES = {
    'login': 'login',
    'checkLogin': 'session',
    'files_filters': 'filters',
    'create_bundle': 'bundle',
    'check_bundle': lambda bundle_id: 'bundle/{}'.format(bundle_id),
    'analysis': lambda bundle_id: 'analysis/{}'.format(bundle_id),
    'upload_files': lambda bundle_id: 'file/{}'.format(bundle_id),
    'error': 'error',
    'diff': lambda parent_id, child_id: 'analysis/{}/{}'.format(parent_id, child_id)
}

DEEPCODE_CONFIG_NAMES = {
    'backend_host': 'BACKEND_HOST',
    'is_logged_in': 'IS_LOGGED_IN',
    'token': 'TOKEN',
    'is_upload_confirmed': 'IS_UPLOAD_CONFIRMED',
    'account_type': 'ACCOUNT_TYPE'
}

DEEPCODE_DEFAULT_CONFIG_FIELDS = {
    DEEPCODE_CONFIG_NAMES['backend_host']: DEEPCODE_BACKEND_HOST,
    DEEPCODE_CONFIG_NAMES['is_logged_in']: False,
    DEEPCODE_CONFIG_NAMES['token']: None,
    DEEPCODE_CONFIG_NAMES['is_upload_confirmed']: False,
    DEEPCODE_CONFIG_NAMES['account_type']: '',
}

CURRENT_FOLDER_PATH = '.'
MAX_BATCH_CONTENT_SIZE = 512000  # 512 kB
MAX_FILE_SIZE = 256000  # 256 kB

GITIGNORE_FILENAME = '.gitignore'
GIT_FOLDERNAME = '.git'

SEVERITIES = {
    1: 'Info',
    2: 'Warning',
    3: 'Critical'
}
