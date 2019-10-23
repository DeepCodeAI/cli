DEEPCODE_CONFIG_FILENAME = '.deepcodeConfig'
DEEPCODE_SOURCE_NAME = {'source': 'cli'}
DEEPCODE_BACKEND_HOST = 'https://www.deepcode.ai'
DEEPCODE_API_PREFIX = 'publicapi'
DEEPCODE_API_ROUTES = {
    'login': '{}/{}/login'.format(DEEPCODE_BACKEND_HOST, DEEPCODE_API_PREFIX),
    'checkLogin': '{}/{}/session'.format(DEEPCODE_BACKEND_HOST, DEEPCODE_API_PREFIX),
    'filters': '{}/{}/filters'.format(DEEPCODE_BACKEND_HOST, DEEPCODE_API_PREFIX),
    'create_bundle': '{}/{}/bundle'.format(DEEPCODE_BACKEND_HOST, DEEPCODE_API_PREFIX),
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
