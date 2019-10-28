# deepcode errors decoration class
import os
import requests
import atexit
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
    is_cli_mode = False

    @classmethod
    def set_mode_for_handling_errors(cls, is_cli_mode):
        cls.is_cli_mode = is_cli_mode

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
                # sending errors reports to deepcode server temporary disabled
                # if type(err).__name__ == cls.ApiException:
                #   cls.send_error_details_to_deepcode(cls.current_err_details)
                if cls.is_cli_mode:
                    except_action(err)
                    os._exit(1)
                else:
                    return except_action(err)

        return decorated_func

    @classmethod
    def return_error_msg_depending_on_mode(cls, error):
        if cls.is_cli_mode:
            print(error)
        else:
            return {'error': error}

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

        if error_name is api_err and str(error) in BACKEND_ERRORS:
            return cls.return_error_msg_depending_on_mode(BACKEND_ERRORS[str(error)])
        else:
            return cls.return_error_msg_depending_on_mode(
                BACKEND_ERRORS['unhandled_error'](error_name, str(error)))

    @classmethod
    def backend_error_decorator(cls, func):
        return cls.DecoratorsFactory(
            func, lambda error: cls.process_backend_error(error))

    @classmethod
    def open_config_file_error_decorator(cls, func):
        return cls.DecoratorsFactory(func, lambda err: cls.return_error_msg_depending_on_mode(OPEN_FILE_ERROR))

    @classmethod
    def parse_api_response_to_json_error_decorator(cls, func):
        return cls.DecoratorsFactory(func, lambda err: cls.return_error_msg_depending_on_mode(
            PARSE_API_RESPONSE_JSON_ERROR))

    @classmethod
    def bundle_path_error_decorator(cls, func):
        def _err_handler(err):
            return cls.return_error_msg_depending_on_mode(PATH_ERRORS[str(err)] if str(err) in PATH_ERRORS else str(err))
        return cls.DecoratorsFactory(func, _err_handler)

    @classmethod
    def files_bundle_error_decorator(cls, func):
        def _err_handler(err):
            file_bundle_err = cls.FilesBundlesException
            error_name = type(err).__name__
            if error_name is file_bundle_err and str(err) in FILES_BUNDLE_ERRORS:
                return cls.return_error_msg_depending_on_mode(FILES_BUNDLE_ERRORS[str(err)])
            else:
                return cls.return_error_msg_depending_on_mode(FILES_BUNDLE_ERRORS['unhandled_error'](error_name, str(err)))
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
