import requests
import json
from deepcode.src.constants.config_constants \
    import DEEPCODE_CONFIG_FILENAME, \
    DEEPCODE_DEFAULT_CONFIG_FIELDS, DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST, DEEPCODE_API_PREFIX, DEEPCODE_API_ROUTES


class DeepCodeHttp:
    def __init__(self, config):
        self.config = config.current_config
        self.base_endpoint = self.config[DEEPCODE_CONFIG_NAMES['backend_host']]
        self.routes_prefix = DEEPCODE_API_PREFIX

    def construct_endpoint(self, route):
        return '{}/{}/{}'.format(self.base_endpoint, self.routes_prefix, route)

    def create_headers(self, options={}, isJson=True, token=True):
        headers = dict()
        if token:
            headers["Session-Token"] = \
                self.config[DEEPCODE_CONFIG_NAMES['token']] or options['token']

        if isJson:
            headers["Content-Type"] = 'application/json'
            if 'charset' in options:
                headers["Content-Type"] += ';charset=utf-8'
        return headers

    def post(self, route, options={}, response_to_json=True):
        headers = self.create_headers(options=options, token=False)\
            if route == DEEPCODE_API_ROUTES['login'] else self.create_headers(options=options)
        response = requests.post(
            self.construct_endpoint(route), json=options['data'], headers=headers)
        return self._proccess_response(response, response_to_json, route)

    def get(self, route, options={}, response_to_json=True):
        headers = self.create_headers(options, isJson=False)
        response = requests.get(
            self.construct_endpoint(route), headers=headers)
        return self._proccess_response(response, response_to_json, route)

    def _proccess_response(self, response, response_to_json, route):
        if response_to_json:
            try:
                return response.json()
            except ValueError:
                raise Exception(
                    'Something happened with parsing json from server: ', route, response)
        return response
