# backend possible errors
BACKEND_ERRORS = {
    'token': 'Missing or invalid sessionToken or incomplete login process',
    'invalid_content': 'Request content doesn’t match the specifications or attempted to upload files to a git bundle',
    'missing_consent': 'Missing open source consent',
    'invalid_bundle_access': 'Unauthorized access to requested bundle or repository',
    'large_payload': 'Payload is too large',
    'expired_bundle': 'Uploaded bundle has expired or unable to resolve requested oid for git repository',
    'invalid_login_response': 'Not valid login server response',
    'invalid_check_login_response': 'Not valid check login status response from server',
    'invalid_bundle_response': 'Not valid bundle response from server',
    'invalid_analysis_response': 'Not valid analysis response from server',
    'analysis_failed': 'Analysis status FAILED.',
    'unhandled_error': lambda err_name, err_msg: '{}: {}'.format(err_name, err_msg),
    'not_confirmed': 'Uploading code is not confirmed'
}

PATH_ERRORS = {
    'invalid_repo_path': 'Not valid repository to analyze',
    'invalid_files_path': 'Path to analyze is not valid',
    'no_path': 'Path does not exist',
    'path_args_error': 'Too much paths or no path provided. Secify either one path for analysis or two paths for diff analysis'
}

FILES_BUNDLE_ERRORS = {
    'too_big': 'FIles bundle is too big to analyze',
    'fail_create_hash': lambda file: 'Failed to create hash of {}'.format(file),
    'unhandled_error': lambda err_name, err_msg: '{}: {}'.format(err_name, err_msg)
}

# custom errors messages, which can be caused while interacting with backend
ANALYSIS_FAIL_ERROR = 'Analysis failed'
OPEN_FILE_ERROR = 'Failed to open deepcode config file'
PARSE_API_RESPONSE_JSON_ERROR = 'Failed to parse json response from server'
