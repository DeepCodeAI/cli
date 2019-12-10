import sys
import argparse
from deepcode.src.constants.cli_constants \
    import CLI_NAME, CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, CLI_SUPPORTED_OPTIONS, SUPPORTED_RESULTS_FORMATS
from deepcode.src.constants.config_constants import DEEPCODE_PACKAGE_VERSION
from deepcode.src.helpers.cli_helpers import CLI_PARSER_HELP_MESSAGES, CLI_MAIN_HELP_DESCRIPTION
from deepcode.src.helpers import errors_messages



class DeepCodeCliHelper(argparse.HelpFormatter):
    def format_help(self):
        return CLI_MAIN_HELP_DESCRIPTION

    def print_help(self):
        pass

    def print_usage(self):
        pass


class DeepCodeArgsParser:

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            prog=CLI_NAME, formatter_class=DeepCodeCliHelper)

        self.subparsers = self.parser.add_subparsers(
            dest=CLI_ARGS_NAMESPACE_NAME)

        [login, logout, analyze, config] = CLI_SUPPORTED_COMMANDS
        [path_option, bundle_type_option, format_option,
            silent_option, version_option] = CLI_SUPPORTED_OPTIONS

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
        self.analyze_parser.add_argument(
            *path_option, type=str, nargs='+'
        )
        self.analyze_parser.add_argument(
            *bundle_type_option, action='store_true')
        self.analyze_parser.add_argument(
            *format_option, choices=SUPPORTED_RESULTS_FORMATS)
        self.analyze_parser.add_argument(
            *silent_option, action='store_true'
        )

        # TODO -v/--version is doing the same thing as -h/--help for now - adapt how?
        self.parser.add_argument(*version_option, action='version', version=DEEPCODE_PACKAGE_VERSION)

    def parse(self):
        if len(sys.argv) == 1:
            self.parser.print_help()
            return {}
        result = vars(self.parser.parse_args())
        return result

    def show_help_for_many_bundles(self):
        print(errors_messages.PATH_ERRORS['path_args_error'])
        self.parser.print_help()
