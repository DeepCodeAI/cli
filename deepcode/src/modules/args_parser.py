import sys
import os
import argparse
from deepcode.src.constants.cli_constants \
    import CLI_NAME, CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, CLI_SUPPORTED_OPTIONS, SUPPORTED_RESULTS_FORMATS
from deepcode.src.helpers.cli_parser_helpers import CLI_PARSER_HELP_MESSAGES


class DeepCodeArgsParser:

    def __init__(self):
      # TODO: add help for options arguments

        self.parser = argparse.ArgumentParser(
            prog=CLI_NAME, description="DeepCode CLI description", epilog="More description in the end")

        self.subparsers = self.parser.add_subparsers(
            help='CLI description', dest=CLI_ARGS_NAMESPACE_NAME)

        [login, logout, analyze, config] = CLI_SUPPORTED_COMMANDS
        [list_option, format_option, path_option] = CLI_SUPPORTED_OPTIONS

        login_help, logout_help, config_help, analyze_help = CLI_PARSER_HELP_MESSAGES.values()

        self.login_parser = self.subparsers.add_parser(
            login, help=login_help)

        self.logou_parser = self.subparsers.add_parser(
            logout, help=logout_help)

        self.config_parser = self.subparsers.add_parser(
            config, help=config_help, aliases=['c'])
        self.config_parser.add_argument(
            *format_option, choices=SUPPORTED_RESULTS_FORMATS, help='list help')

        self.analyze_parser = self.subparsers.add_parser(
            analyze, help=analyze_help, aliases=['a'])
        self.analyze_parser.add_argument(
            *path_option, type=str, help='path to analyze')
        self.analyze_parser.add_argument(
            *format_option, choices=SUPPORTED_RESULTS_FORMATS, help='list help')

    def parse(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            return {}
        return vars(self.parser.parse_args())
