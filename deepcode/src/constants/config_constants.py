DEEPCODE_PACKAGE_NAME = 'deepcode'
DEEPCODE_PACKAGE_VERSION = '0.0.8'
DEEPCODE_CONFIG_FILENAME = '.dcconfig.json'
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
    'backend_host': 'service_url',
    'token': 'token',
}

MAX_REQUEST_BODY_SIZE = 4 * 1024 * 1024  # 4MB

GITIGNORE_FILENAME = '.gitignore'
GIT_FOLDERNAME = '.git'

SEVERITIES = {
    1: 'Info',
    2: 'Warning',
    3: 'Critical'
}
