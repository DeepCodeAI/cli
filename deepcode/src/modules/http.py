import requests
import json

from deepcode.src.modules.errors_handler import DeepCodeErrorHandler

from deepcode.src.constants.config_constants import (
    DEEPCODE_API_ROUTES, DEEPCODE_API_PREFIX, DEEPCODE_BACKEND_HOST
)
from deepcode.src.constants.backend_constants import BACKEND_STATUS_CODES


class DeepCodeHttp:
    def __init__(self, config):
        self.config = config.current_config
        self.base_endpoint = self.config.get('backend_host') or DEEPCODE_BACKEND_HOST
        self.routes_prefix = DEEPCODE_API_PREFIX

    def construct_endpoint(self, route):
        return '{}/{}/{}'.format(self.base_endpoint, self.routes_prefix, route)

    def create_headers(self, options={}, isJson=True, token=True):
        headers = dict()
        if token:
            headers["Session-Token"] = \
                self.config.get('token') or options['token']

        if isJson:
            headers["Content-Type"] = 'application/json'
            if 'charset' in options:
                headers["Content-Type"] += ';charset=utf-8'
        return headers

    def post(self, route, options={}, response_to_json=True):
        with_token = True
        if route == DEEPCODE_API_ROUTES['login']:
            with_token = False
        headers = self.create_headers(options=options, token=with_token)
        response = requests.post(
            self.construct_endpoint(route), json=options['data'], headers=headers)
        self.check_response_status_code(response, route)
        return self._proccess_response(response, response_to_json, route)

    def get(self, route, options={}, response_to_json=True):
        headers = self.create_headers(options)
        response = requests.get(
            self.construct_endpoint(route), headers=headers)
        self.check_response_status_code(response, route)
        return self._proccess_response(response, response_to_json, route)

    @DeepCodeErrorHandler.parse_api_response_to_json_error_decorator
    def _proccess_response(self, response, response_to_json, route):
        return response.json() if response_to_json else response

    @DeepCodeErrorHandler.backend_error_decorator
    def check_response_status_code(self, response, route=''):
        codes_ignores = {
            'check_login':
                response.status_code == BACKEND_STATUS_CODES['login_in_progress']
                and route == DEEPCODE_API_ROUTES['checkLogin'],
            'big_upload_for_missing_files':
                response.status_code == BACKEND_STATUS_CODES['large_payload']
                and route == DEEPCODE_API_ROUTES['upload_files']
        }
        if response.status_code is not BACKEND_STATUS_CODES['success']:
            if codes_ignores['check_login'] \
                    or codes_ignores['big_upload_for_missing_files']:
                return
            if response.status_code in BACKEND_STATUS_CODES.values():
                error_type =\
                    [name for name, code in BACKEND_STATUS_CODES.items()
                     if code == response.status_code][0]
            else:
                error_type = str(response)
            DeepCodeErrorHandler.raise_backend_error(error_type,
                                                     err_details=DeepCodeErrorHandler.construct_backend_error_for_report(
                                                         route, response, error_type
                                                     ))
