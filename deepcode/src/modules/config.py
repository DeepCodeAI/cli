import os
import json
from deepcode.src.constants.config \
    import DEEPCODE_CONFIG_FILENAME, DEEPCODE_DEFAULT_CONFIG_FIELDS, DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST
from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS


class DeepCodeConfig:
    def __init__(self):
        self.config_path = self.default_config_path()
        if not self.config_exists():
            self.update_config_file()
        self.current_config = self.get_config_from_file()
        print('config when script starts: ', self.current_config)

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

    def config_to_json(self):
        return json.dumps(self.current_config)

    def config_to_txt(self):
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

    def config_actions(self, command_options):
        [json_format, txt_format] = SUPPORTED_RESULTS_FORMATS
        chosen_format = command_options['format']
        if not chosen_format:
            print('You can configure backend host and change it for your own')
            new_backend_host = input(
                'Enter new backend host or leave blank for default({}): '.format(DEEPCODE_BACKEND_HOST))
            if new_backend_host:
                # validate last slash
                if new_backend_host[len(new_backend_host)-1] == '/':
                    new_backend_host = new_backend_host[:len(
                        new_backend_host)-1]
                self.update_backend_host(new_backend_host)
                print('Backend host updated')
        if chosen_format == json_format:
            print(self.config_to_json())
        if chosen_format == txt_format:
            print(self.config_to_txt())
