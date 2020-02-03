import os
import json
from deepcode.src.modules.errors_handler import DeepCodeErrorHandler

from deepcode.src.utils.config_utils import handle_backend_host_last_slash

from deepcode.src.constants.config_constants import DEEPCODE_CONFIG_FILENAME, DEEPCODE_CONFIG_NAMES
from deepcode.src.helpers.cli_helpers import CONFIG_SETTINGS_MESSAGES


class deepcodeconfig:
    def __init__(self):
        self.config_path = self.default_config_path()
        if not self.config_exists():
            self.update_config_file()
        self.current_config = self.get_config_from_file()

    def default_config_path(self):
        return os.path.join(os.path.expanduser('~'), DEEPCODE_CONFIG_FILENAME)

    @DeepCodeErrorHandler.open_config_file_error_decorator
    def update_config_file(self, config=None):
        with open(self.config_path, 'w') as config_file:
            json.dump(config or {}, config_file, indent=2)

    def config_exists(self):
        return os.path.exists(self.config_path)

    @DeepCodeErrorHandler.open_config_file_error_decorator
    def get_config_from_file(self):
        with open(self.config_path) as config_file:
            return json.load(config_file)

    def update_config(self, new_fields={}):
        for field in new_fields:
            self.current_config[DEEPCODE_CONFIG_NAMES[field]
                                ] = new_fields[field]
        self.update_config_file(self.current_config)

    def delete_user_config(self, update_file=True):
        self.current_config[DEEPCODE_CONFIG_NAMES['token']] = ''
        if update_file:
            self.update_config_file(self.current_config)

    def update_backend_host(self, new_host):
        self.delete_user_config(update_file=False)
        self.update_config({'backend_host': new_host})

    def set_user_login_config(self, token):
        logged_in_config = {
            'token': token,
        }
        self.update_config(logged_in_config)

    def is_user_logged_in(self):
        return bool(self.current_config.get(DEEPCODE_CONFIG_NAMES['token']))

    def configure_cli(self):
        new_backend_host = input(CONFIG_SETTINGS_MESSAGES['configure_backend_host'])
        processed_host = new_backend_host and handle_backend_host_last_slash(new_backend_host) or ''
        self.update_backend_host(processed_host)
        print(CONFIG_SETTINGS_MESSAGES['backend_host_success_update'](processed_host))
