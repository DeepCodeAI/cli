import requests
import json

# Temporary here for tests


class Errors:
    @classmethod
    def http_error_decorator(cls, func):
        def decorated_func(*args, **kwargs):
            try:
                result = func()
                return result
            except:
                print('IN EXCEPT')
                cls.handle_error()
        return decorated_func

    @classmethod
    def handle_error(cls):
        print('in handler', cls)


class DeepCodeHttp:
    def __init__(self):
        pass

    def create_token_header(self, token=''):
        return {"Session-Token": token}

    def create_headers(self, options={}):
        headers = dict()
        if not len(options):
            return headers
        if 'token' in options:
            headers["Session-Token"] = options['token']
        if 'content_type_json' in options:
            headers["Content-Type"] = 'application/json'
        return headers

    # @Errors.http_error_decorator
    def post(self, endpoint, options={}):
        data = options['data']
        response = requests.post(
            endpoint, data=data, headers=self.create_headers(options))
        return response.json()

    def get(self, endpoint, options):
        response = requests.get(endpoint, headers=self.create_headers(options))
        return response

    def put(self, endpoint, options):
        pass
