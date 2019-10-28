# deepcode errors decoration class
import os
import requests
from deepcode.src.constants.config_constants import DEEPCODE_API_ROUTES, DEEPCODE_API_PREFIX, DEEPCODE_BACKEND_HOST, DEEPCODE_SOURCE_NAME
from deepcode.src.helpers.errors_messages \
    import BACKEND_ERRORS, OPEN_FILE_ERROR, PARSE_API_RESPONSE_JSON_ERROR, PATH_ERRORS, FILES_BUNDLE_ERRORS
from deepcode.src.constants.backend_constants import BACKEND_STATUS_CODES
from deepcode.src.helpers.errors_messages import BACKEND_ERRORS


class DeepCodeErrors:

    ApiException = 'ApiException'
    PathExeption = 'PathExeption'
    FilesBundlesException = 'FilesBundlesException'
    current_err_details = {}

    @classmethod
    def ExceptionsFactory(cls, exception_name):
        class FactoryExeption(Exception):
            def __init__(self, message):
                super().__init__(message)
        FactoryExeption.__name__ = exception_name
        return FactoryExeption

    @classmethod
    def DecoratorsFactory(cls, func_to_decorate, except_action):
        def decorated_func(*args, **kwargs):
            try:
                return func_to_decorate(*args, **kwargs)
            except BaseException as err:
                except_action(err)
                # sending errors reports to deepcode server temporary disabled
                # if type(err).__name__ == cls.ApiException:
                #   cls.send_error_details_to_deepcode(cls.current_err_details)
                os._exit(1)

        return decorated_func

    @classmethod
    def raise_backend_error(cls, e_type, err_details={}):
        cls.current_err_details = err_details
        raise cls.ExceptionsFactory(cls.ApiException)(e_type)

    @classmethod
    def raise_path_error(cls, e_type):
        raise cls.ExceptionsFactory(cls.PathExeption)(e_type)

    @classmethod
    def raise_files_bundle_error(cls, e_type): raise cls.ExceptionsFactory(
        cls.FilesBundlesException)(e_type)

    @classmethod
    def process_backend_error(cls, error):
        api_err = cls.ApiException
        error_name = type(error).__name__

        if not len(cls.current_err_details):
            cls.current_err_details = {'error': error}

        print('NOW', error_name, error, cls.current_err_details)
        if error_name is api_err and str(error) in BACKEND_ERRORS:
            print(error_name, BACKEND_ERRORS[str(error)])
        else:
            print(BACKEND_ERRORS['unhandled_error'](error_name, str(error)))

    @classmethod
    def backend_error_decorator(cls, func):
        return cls.DecoratorsFactory(
            func, lambda error: cls.process_backend_error(error))

    @classmethod
    def open_config_file_error_decorator(cls, func):
        return cls.DecoratorsFactory(func, lambda err: print(OPEN_FILE_ERROR))

    @classmethod
    def parse_api_response_to_json_error_decorator(cls, func):
        return cls.DecoratorsFactory(func, lambda err: print(
            PARSE_API_RESPONSE_JSON_ERROR))

    @classmethod
    def bundle_path_error_decorator(cls, func):
        def _err_handler(err):
            print(PATH_ERRORS[str(err)])
        return cls.DecoratorsFactory(func, _err_handler)

    @classmethod
    def files_bundle_error_decorator(cls, func):
        def _err_handler(err):
            file_bundle_err = cls.FilesBundlesException
            error_name = type(err).__name__
            if error_name is file_bundle_err and str(err) in FILES_BUNDLE_ERRORS:
                print(error_name, FILES_BUNDLE_ERRORS[str(err)])
            else:
                print(FILES_BUNDLE_ERRORS['unhandled_error'](
                    error_name, str(err)))
        return cls.DecoratorsFactory(func, _err_handler)

    @staticmethod
    def construct_backend_error_for_report(route, data, error_name):
        return {
            'data': data,
            'endpoint': route,
            'error': BACKEND_ERRORS[error_name]
        }

    @staticmethod
    def send_error_details_to_deepcode(err_details):
        err_route = '{}/{}/{}'.format(DEEPCODE_BACKEND_HOST,
                                      DEEPCODE_API_PREFIX, DEEPCODE_API_ROUTES['error'])
        err_details['source'] = DEEPCODE_SOURCE_NAME['source']
        requests.post(
            err_route,
            json=err_details,
            headers={
                "Content-Type": "application/json"
            }
        )
