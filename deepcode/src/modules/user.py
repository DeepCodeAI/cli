import json
import time
import requests
from deepcode.src.constants.config_constants \
    import DEEPCODE_DEFAULT_CONFIG_FIELDS, DEEPCODE_API_ROUTES, DEEPCODE_SOURCE_NAME, DEEPCODE_CONFIG_NAMES

from deepcode.src.utils.api_utils import validate_login_response, validate_check_login_response


class DeepCodeUser:
    def __init__(self, http):
        self.http = http

    def login(self):
        user_login_data = self.http.post(DEEPCODE_API_ROUTES['login'], {
            'data': DEEPCODE_SOURCE_NAME})
        if validate_login_response(user_login_data):
            return user_login_data
        raise Exception('Not valid response from server when login')

    # TODO: errors decoration

    def check_login(self, token):
        MAX_POLLS_LIMIT = 1000
        POLLING_INTERVAL = 1  # 1sec
        for _ in range(MAX_POLLS_LIMIT):
            response = self.http.get(
                DEEPCODE_API_ROUTES['checkLogin'], {'token': token}, response_to_json=False)
            if response.status_code == requests.codes['unauthorized']:
                raise Exception('Unatorized user, failed to check login')
            if response.status_code == requests.codes['ok']:
                check_result = response.json()
                if validate_check_login_response(check_result):
                    return check_result['type']
                raise Exception(
                    'Not valid response from server while check login status')
            time.sleep(POLLING_INTERVAL)

    def confirm_code_upload(self):
        positive_response_types = ('y', 'Y')
        confirm_upload_user_response = input(
            'Please confirm uploading code to DeepCode server.\n Do you confirm? (y/n): ')
        is_positive_user_response = confirm_upload_user_response in positive_response_types
        if is_positive_user_response:
            print('You successfully confirmed uploading code to DeepCode server')
        else:
            print('You denided uploading code to deepcode server')
        return is_positive_user_response
