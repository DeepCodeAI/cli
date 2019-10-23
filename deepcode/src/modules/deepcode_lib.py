import json

from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.config import DeepCodeConfig
from deepcode.src.modules.args_parser import DeepCodeArgsParser
from deepcode.src.modules.http import DeepCodeHttp
from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS
from deepcode.src.constants.config import DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST


class DeepCodeLib:
    def __init__(self, isCliMode=False):
        self.isCliMode = isCliMode
        if self.isCliMode:
            self.args_parser = DeepCodeArgsParser()

        self.user = DeepCodeUser()
        self.config = DeepCodeConfig()
        self.http = DeepCodeHttp()

    def activate_cli(self):
        cli_args_dict = self.args_parser.parse()
        if (len(cli_args_dict)):
            self.process_cli_args(cli_args_dict)

    def process_cli_args(self, cli_args_dict):
        command = cli_args_dict[CLI_ARGS_NAMESPACE_NAME]
        [login, logout, analyze, config] = CLI_SUPPORTED_COMMANDS

        command_trigger = {
            login: lambda: self.user.login_actions(self),
            logout: lambda: self.user.logout_actions(self),
            config: lambda: self.config.config_actions(cli_args_dict),
            analyze: lambda: print('analyze logic')
        }
        command_trigger[command]()
