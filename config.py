"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import json
import os

REQUIRED_CONFIG_PARAMS = ['dc_server_host', 'dc_server_port']
DEFAULT_HOST = 'https://www.deepcode.ai'
DEFAULT_PORT = 443


class Config:
    def __init__(self, config_path):
        self.path = config_path
        self.data = {}

    def parse(self):
        try:
            with open(self.path, 'r') as f:
                self.data = json.load(f)
        except ValueError:
            raise ConfigError('Could not parse the configuration file ({}) as json.'.format(self.path))
        except FileNotFoundError:
            raise ConfigError('Could not find configuration file "{}".'.format(self.path))

        for required in REQUIRED_CONFIG_PARAMS:
            if required not in self.data:
                raise ConfigError('"{}" is a required configuration parameter, '
                                  'but was not found in the configuration file {}.'.format(required, self.path))

    def serialize(self):
        with open(self.path, 'w') as f:
            json.dump(self.data, f, sort_keys=True, indent=2)

    def set_session_token(self, value):
        self.data['session_token'] = value
        self.serialize()

    def delete_session_token(self):
        if 'session_token' in self.data:
            del self.data['session_token']
            self.serialize()

    def configuration_exists(self):
        return os.path.exists(self.path)


class ConfigError(ValueError):
    pass


class ConfigWizard:
    def __init__(self, config):
        self.config = config

    def create_config(self):
        print('creating a new configuration file {}'.format(self.config.path))
        self._get_user_input_and_serialize(DEFAULT_HOST, DEFAULT_PORT, current_name='default')

    def update_config(self):
        print('updating configuration file {}'.format(self.config.path))
        current_host = self.config.data['dc_server_host']
        current_port = self.config.data['dc_server_port']
        self._get_user_input_and_serialize(current_host, current_port, current_name='current')

    def _get_user_input_and_serialize(self, default_host, default_port, current_name):
        print('leave empty to use {} values'.format(current_name))
        host = input('DeepCode server host ({}: {}): '.format(current_name, default_host))
        if host == '':
            host = default_host
        if default_host == host:
            shown_port = default_port
        else:
            current_name = 'suggested'
            shown_port = 80 if host.startswith('http://') else 443
        port = input('DeepCode server port ({}: {}): '.format(current_name, shown_port))
        if port == '':
            port = shown_port
        else:
            port = str(port)
        self.config.data['dc_server_host'] = host
        self.config.data['dc_server_port'] = port
        self.config.serialize()
        print('configuration stored in {}'.format(self.config.path))
