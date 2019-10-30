import json
import time

from deepcode.src.modules.errors_handler import ErrorHandler
from deepcode.src.constants.backend_constants import MAX_POLLS_LIMIT, POLLING_INTERVAL, BACKEND_STATUS_CODES
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES, DEEPCODE_SOURCE_NAME
from deepcode.src.utils.api_utils import validate_login_response, validate_check_login_response
from deepcode.src.helpers.cli_helpers import CONFRIM_UPLOAD_HELPERS


class DeepCodeUser:
    def __init__(self, http):
        self.http = http

    @ErrorHandler.backend_error_decorator
    def login(self):
        user_login_data = self.http.post(DEEPCODE_API_ROUTES['login'], {
            'data': DEEPCODE_SOURCE_NAME})
        if not validate_login_response(user_login_data):
            ErrorHandler.raise_backend_error('invalid_login_response',
                                             err_details=ErrorHandler.construct_backend_error_for_report(
                                                 DEEPCODE_API_ROUTES['login'], user_login_data, 'invalid_login_response'))
        return user_login_data

    @ErrorHandler.backend_error_decorator
    def check_login(self, token):
        for _ in range(MAX_POLLS_LIMIT):
            response = self.http.get(
                DEEPCODE_API_ROUTES['checkLogin'], {'token': token}, response_to_json=False)
            if response.status_code == BACKEND_STATUS_CODES['success']:
                check_result = response.json()
                if validate_check_login_response(check_result):
                    return check_result['type']
                ErrorHandler.raise_backend_error(
                    'invalid_check_login_response',
                    err_details=ErrorHandler.construct_backend_error_for_report(
                        DEEPCODE_API_ROUTES['checkLogin'], check_result, 'invalid_check_login_response'))
            time.sleep(POLLING_INTERVAL)

    def confirm_code_upload(self):
        positive_response_types = ('y', 'Y')
        confirm_upload_user_response = input(CONFRIM_UPLOAD_HELPERS['confirm'])
        is_positive_user_response = confirm_upload_user_response in positive_response_types
        print(
            CONFRIM_UPLOAD_HELPERS['success' if is_positive_user_response else 'fail'])
        return is_positive_user_response
