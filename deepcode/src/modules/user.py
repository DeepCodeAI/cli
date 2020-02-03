import json
import time

from deepcode.src.modules.errors_handler import DeepCodeErrorHandler
from deepcode.src.utils.api_utils import validate_login_response

from deepcode.src.constants.backend_constants import MAX_POLLS_LIMIT, POLLING_INTERVAL, BACKEND_STATUS_CODES
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES, DEEPCODE_SOURCE_NAME


class DeepCodeUser:
    def __init__(self, http):
        self.http = http

    @DeepCodeErrorHandler.backend_error_decorator
    def login(self):
        user_login_data = self.http.post(DEEPCODE_API_ROUTES['login'], {
            'data': DEEPCODE_SOURCE_NAME})
        if not validate_login_response(user_login_data):
            DeepCodeErrorHandler.raise_backend_error('invalid_login_response',
                                                     err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                                                         DEEPCODE_API_ROUTES['login'], user_login_data, 'invalid_login_response'))
        return user_login_data

    @DeepCodeErrorHandler.backend_error_decorator
    def check_login(self, token):
        for _ in range(MAX_POLLS_LIMIT):
            response = self.http.get(
                DEEPCODE_API_ROUTES['checkLogin'], {'token': token}, response_to_json=False)
            if response.status_code == BACKEND_STATUS_CODES['success']:
                return True
            time.sleep(POLLING_INTERVAL)
        return False
