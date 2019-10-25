import os
import json
from deepcode.src.constants.config_constants \
    import DEEPCODE_CONFIG_FILENAME, DEEPCODE_DEFAULT_CONFIG_FIELDS, DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST
from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS


class DeepCodeConfig:
    def __init__(self, isCliMode=False):
        self.isCliMode = isCliMode
        self.config_path = self.default_config_path()
        if not self.config_exists():
            self.update_config_file()
        self.current_config = self.get_config_from_file()
        # print('config when script starts: ', self.current_config)

    def default_config_path(self):
        return os.path.join(os.path.expanduser('~'), DEEPCODE_CONFIG_FILENAME)

    def update_config_file(self, config=None):
        with open(self.config_path, 'w') as config_file:
            json.dump(config or DEEPCODE_DEFAULT_CONFIG_FIELDS, config_file)

    def config_exists(self):
        return os.path.exists(self.config_path)

    def get_config_from_file(self):
        with open(self.config_path) as config_file:
            return json.load(config_file)

    def display_config_to_json(self):
        return json.dumps(self.current_config)

    def display_config_to_txt(self):
        result = ''
        for index, key in enumerate(self.current_config):
            result += '{}={}{}'.format(key, self.current_config[key],
                                       '\n' if index != (len(self.current_config)-1) else '')
        return result

    def update_config(self, new_fields={}):
        for field in new_fields:
            self.current_config[DEEPCODE_CONFIG_NAMES[field]
                                ] = new_fields[field]
        self.update_config_file(self.current_config)

    def delete_user_config(self, update_file=True):
        self.current_config[DEEPCODE_CONFIG_NAMES['is_logged_in']] = False
        self.current_config[DEEPCODE_CONFIG_NAMES['token']] = ''
        self.current_config[DEEPCODE_CONFIG_NAMES['account_type']] = ''
        self.current_config[DEEPCODE_CONFIG_NAMES['is_upload_confirmed']] = False
        if update_file:
            self.update_config_file(self.current_config)

    def update_backend_host(self, new_host):
        self.delete_user_config(update_file=False)
        self.update_config({'backend_host': new_host})

    def set_user_login_config(self, token, account_type, upload_confrm):
        logged_in_config = {
            'token': token,
            'is_logged_in': True,
            'account_type': account_type
        }
        if upload_confrm:
            logged_in_config['is_upload_confirmed'] = True
        self.update_config(logged_in_config)

    def is_user_logged_in(self):
        return self.current_config[DEEPCODE_CONFIG_NAMES['is_logged_in']]

    def is_code_upload_confirmed(self):
        return self.current_config[DEEPCODE_CONFIG_NAMES['is_upload_confirmed']]

    def activate_code_upload(self):
        self.current_config[DEEPCODE_CONFIG_NAMES['is_upload_confirmed']] = True
        self.update_config_file(self.current_config)
