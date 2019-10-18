"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import argparse
import os
import json

from dc_analysis import DCAnalysisCLIPrinter, DCAnalysisJsonPrinter
from config import Config, ConfigError, ConfigWizard


def default_config_path():
    return os.path.join(os.path.expanduser('~'), '.deepcodecli')


def create_default_config_if_not_exists(config, json_mode):
    print({config, json_mode})
    if not os.path.exists(config):
        if not json_mode:
            ConfigWizard(config).create_config()
        else:
            default_config = {
                'dc_server_host': 'https://www.deepcode.ai'}
            with open(config, 'w') as f:
                json.dump(default_config, f)


def print_error_and_exit(error, json_mode):
    if json_mode:
        print(json.dumps({'error': error}))
    else:
        print('Error: {}'.format(error))
    exit(1)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '--config',
                        help='path to configuration file (default ~/.deepcodecli)',
                        default=default_config_path())
    parser.add_argument('task',
                        type=str,
                        choices=['login', 'logout', 'analyze',
                                 'diff', 'wait_for_login', 'config'],
                        help='task to execute')
    parser.add_argument('bundle',
                        nargs='*',
                        help='one or two bundles, either directories or '
                             '(repo/owner/hash) in the currently logged in platform')
    parser.add_argument('--json',
                        help='whether to print in human readable format or json',
                        action='store_true')
    cli_args = parser.parse_args()
    config = Config(cli_args.config)

    if not config.configuration_exists():
        if cli_args.json:
            error_msg = 'Provided configuration file {} does not exist'.format(
                config.path)
            print_error_and_exit(error_msg, cli_args.json)
        else:
            ConfigWizard(config).create_config()
        return

    try:
        config.parse()
    except ConfigError as error:
        print_error_and_exit(error, cli_args.json)

    if cli_args.json:
        dc_printer = DCAnalysisJsonPrinter(config)
    else:
        dc_printer = DCAnalysisCLIPrinter(config)

    if cli_args.task == 'login':
        dc_printer.login()
    elif cli_args.task == 'logout':
        dc_printer.logout()
    elif cli_args.task == 'wait_for_login':
        if not cli_args.json:
            print_error_and_exit(
                'Wait for login is only supported in json mode', cli_args.json)
        dc_printer.wait_for_login()
    elif cli_args.task == 'analyze':
        if len(cli_args.bundle) is 1:
            dc_printer.analyze(cli_args.bundle[0])
        elif len(cli_args.bundle) is 2:
            dc_printer.diff(cli_args.bundle[0], cli_args.bundle[1])
        else:
            error_msg = 'Unsupported number of bundles provided: {}'.format(
                len(cli_args.bundle))
            print_error_and_exit(error_msg, cli_args.json)
    elif cli_args.task == 'diff':
        if not len(cli_args.bundle) is 2:
            error_msg = 'Unsupported number of bundles provided: {}, expected 2'.format(
                len(cli_args.bundle))
            print_error_and_exit(error_msg, cli_args.json)
        dc_printer.diff(cli_args.bundle[0], cli_args.bundle[1])
    elif cli_args.task == 'config':
        if cli_args.json:
            print_error_and_exit(
                'Creating or altering configurations is not supported in json mode', cli_args.json)
        else:
            ConfigWizard(config).update_config()


if __name__ == '__main__':
    main()
