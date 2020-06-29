# ================ Connection =================

DEFAULT_SERVICE_URL = 'https://www.deepcode.ai'
NETWORK_RETRY_DELAY = 5
DEFAULT_SOURCE = 'cli'

# BACKEND_STATUS_CODES = {
#     'success': 200,
#     'login_in_progress': 304,
#     'token': 401,
#     'invalid_content': 400,
#     'invalid_bundle_access': 403,
#     'expired_bundle': 404,
#     'large_payload': 413
# }

# ================ Analysis =================

ANALYSIS_PROGRESS_INTERVAL = 2
ANALYSIS_RETRY_DELAY = 5
ANALYSIS_RETRIES = 3

# ================ Authentication =================

AUTH_POLLING_INTERVAL = 2

# ================ Files =================

IGNORES_DEFAULT = {
    '**/.git',
}

IGNORE_FILES_NAMES = {
    '.gitignore',
    '.hgignore',
    '.p4ignore',
    '.cvsignore',
    '.dcignore'
}

MULTI_SYNTAX_IGNORE_FILES_NAMES = {
    '.hgignore'
}

MAX_BUCKET_SIZE = 1024 * 1024 * 4

# ================ CLI =================

CONFIG_FILE_PATH = '~/.deepcode.json'

SERVICE_URL_ENV = 'DEEPCODE_SERVICE_URL'
API_KEY_ENV = 'DEEPCODE_API_KEY'
SOURCE_ENV = 'DEEPCODE_SOURCE'
