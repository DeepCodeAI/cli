import os
import requests
import json

from deepcode.src.utils.config_utils import is_package_in_dev_mode
from deepcode.src.constants.config_constants \
    import DEEPCODE_API_ROUTES, DEEPCODE_API_PREFIX, DEEPCODE_BACKEND_HOST, DEEPCODE_SOURCE_NAME, DEEPCODE_CONFIG_NAMES
from deepcode.src.helpers.errors_messages \
    import BACKEND_ERRORS, OPEN_FILE_ERROR, PARSE_API_RESPONSE_JSON_ERROR, PATH_ERRORS, FILES_BUNDLE_ERRORS


class ModuleModeException(Exception):
    pass


# errors decoration class
class DeepCodeErrorHandler:

    ApiException = 'ApiException'
    PathExeption = 'PathExeption'
    FilesBundlesException = 'FilesBundlesException'
    current_err_details = {}
    is_cli_mode = False
    backend_host = None

    @classmethod
    def set_current_err_details(cls, error):
        if not len(cls.current_err_details):
            cls.current_err_details = {'error': error}

    @classmethod
    def set_mode_for_handling_errors(cls, is_cli_mode, config):
        cls.is_cli_mode = is_cli_mode
        cls.backend_host = config.current_config[DEEPCODE_CONFIG_NAMES['backend_host']]

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
                if type(err).__name__ == cls.ApiException:
                    cls.send_error_details_to_deepcode(cls.current_err_details)
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
            cls.set_current_err_details(error)
            raise ModuleModeException

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

        cls.set_current_err_details(error)
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

    @classmethod
    def module_mode_error_decorator(cls, func):
        def _err_handler(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ModuleModeException:
                return json.dumps({'error': cls.current_err_details['error']})
        return _err_handler

    @staticmethod
    def construct_backend_error_for_report(route, data, error_name):
        return {
            'data': data,
            'endpoint': route,
            'error': BACKEND_ERRORS[error_name] if error_name in BACKEND_ERRORS else error_name
        }

    @classmethod
    def send_error_details_to_deepcode(cls, err_details):
        # sending errors to deepcode server only for production mode
        if is_package_in_dev_mode():
            return
        err_route = '{}/{}/{}'.format(DEEPCODE_BACKEND_HOST,
                                      DEEPCODE_API_PREFIX, DEEPCODE_API_ROUTES['error'])
        err_details['source'] = DEEPCODE_SOURCE_NAME['source']
        if 'endpoint' in err_details:
            err_details['endpoint'] = '{}/{}/{}'.format(
                cls.backend_host, DEEPCODE_API_PREFIX, err_details['endpoint'])
        requests.post(
            err_route,
            json=err_details,
            headers={
                "Content-Type": "application/json"
            }
        )
