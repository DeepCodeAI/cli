import json
import time
import requests
from deepcode.src.constants.config \
    import DEEPCODE_DEFAULT_CONFIG_FIELDS, DEEPCODE_API_ROUTES, DEEPCODE_SOURCE_NAME, DEEPCODE_CONFIG_NAMES


class DeepCodeUser:
    def __init__(self):
        pass

    def login_actions(self, lib):

        is_user_logged_in = lib.config.current_config[DEEPCODE_CONFIG_NAMES['is_logged_in']]
        is_upload_confirmed = lib.config.current_config[DEEPCODE_CONFIG_NAMES['is_upload_confirmed']]
        if is_user_logged_in:
            if not is_upload_confirmed:
                print('User is Already logged in, but code upload is not confirmed')
                self.confirm_code_upload(lib)
            else:
                print('User is Already logged in')
            return

        # login
        login_data = self.login(lib)
        [token, login_url] = login_data.values()
        print('Please follow this url to login: {}'.format(login_url))
        # check login
        login_account_type = self.check_login(lib, token)
        # here we have token, we are already logged in, we can write to config
        new_config_data = {
            'token': token,
            'is_logged_in': True,
            'account_type': login_account_type
        }
        print('You are succesfully logged in')
        lib.config.update_config(new_config_data)
        self.confirm_code_upload(lib)

    # TODO: errors decoration

    def login(self, lib):
        user_login_data = lib.http.post(DEEPCODE_API_ROUTES['login'], {
            'data': json.dumps(DEEPCODE_SOURCE_NAME)})
        # TODO: refactor this later
        if 'sessionToken' in user_login_data and 'loginURL' in user_login_data:
            return user_login_data
        raise Exception('Not valid response from server when login')

    # TODO: errors decoration
    def check_login(self, lib, token):
        MAX_POLLS_LIMIT = 1000
        POLLING_INTERVAL = 1  # 1sec
        for _ in range(MAX_POLLS_LIMIT):
            response = lib.http.get(
                DEEPCODE_API_ROUTES['checkLogin'], {'token': token})
            print(response.status_code)
            if response.status_code == requests.codes['unauthorized']:
                raise Exception('Unatorized user, failed to check login')
            if response.status_code == requests.codes['ok']:
                check_result = response.json()
                if 'type' in check_result:
                    return check_result['type']
                raise Exception(
                    'Not valid response from server while check login status')
            time.sleep(POLLING_INTERVAL)

    def confirm_code_upload(self, lib):
        positive_response_types = ('y', 'Y')
        confirm_upload_user_response = input(
            'Please confirm uploading code to DeepCode server.\n Do you confirm? (y/n): ')
        is_positive_user_response = confirm_upload_user_response in positive_response_types
        if is_positive_user_response:
            print('You successfully confirmed uploading code to DeepCode server')
            lib.config.update_config({'is_upload_confirmed': True})
        else:
            print('You denided uploading code to deepcode server')
        return is_positive_user_response

    def is_code_upload_confirmed(self, lib):
        return lib.config.current_config['IS_UPLOAD_CONFIRMED']

    def logout_actions(self, lib):
        lib.config.delete_user_config()
