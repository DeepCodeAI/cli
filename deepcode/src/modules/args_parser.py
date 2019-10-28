import sys
import os
import argparse
from deepcode.src.constants.cli_constants \
    import CLI_NAME, CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, CLI_SUPPORTED_OPTIONS, SUPPORTED_RESULTS_FORMATS
from deepcode.src.helpers.cli_helpers import CLI_PARSER_HELP_MESSAGES, CLI_MAIN_HELP_DESCRIPTION


class DeepCodeCliHelper(argparse.HelpFormatter):
    def format_help(self):
        return CLI_MAIN_HELP_DESCRIPTION


class DeepCodeArgsParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=CLI_NAME, formatter_class=DeepCodeCliHelper)

        self.subparsers = self.parser.add_subparsers(
            dest=CLI_ARGS_NAMESPACE_NAME)

        [login, logout, analyze, config] = CLI_SUPPORTED_COMMANDS
        [bundle_type_option, format_option, path_option] = CLI_SUPPORTED_OPTIONS

        login_help, logout_help, config_help, analyze_help = CLI_PARSER_HELP_MESSAGES.values()

        self.login_parser = self.subparsers.add_parser(login, help=login_help)

        self.logou_parser = self.subparsers.add_parser(
            logout, help=logout_help)

        self.config_parser = self.subparsers.add_parser(
            config, help=config_help, aliases=['c'])
        self.config_parser.add_argument(
            *format_option, choices=SUPPORTED_RESULTS_FORMATS)

        self.analyze_parser = self.subparsers.add_parser(
            analyze, help=analyze_help, aliases=['a'])
        self.analyze_parser.add_argument(*path_option, type=str)
        self.analyze_parser.add_argument(
            *bundle_type_option, action='store_true')
        self.analyze_parser.add_argument(
            *format_option, choices=SUPPORTED_RESULTS_FORMATS)

    def parse(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            return {}
        return vars(self.parser.parse_args())
