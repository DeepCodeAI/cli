from deepcode.src.constants.backend_constants \
    import LOGIN_RESPONSE_FIELDS, CHECK_LOGIN_RESPONSE_FIELDS, BUNDLE_RESPONSE_FIELDS, ANALYSIS_RESPONSE_FIELDS


def validate_login_response(response):
    token, login_url = LOGIN_RESPONSE_FIELDS
    return token in response and login_url in response


def validate_check_login_response(response):
    account_type = CHECK_LOGIN_RESPONSE_FIELDS
    return account_type in response


def validate_remote_bundle_response(response):
    bundle_id, *_ = BUNDLE_RESPONSE_FIELDS
    return bundle_id in response


def validate_analysis_response(response):
    status, progress, analysisURL, results = ANALYSIS_RESPONSE_FIELDS
    return \
        status in response and\
        progress in response and\
        analysisURL in response
