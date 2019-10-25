# python modules
import json
import webbrowser
# own modules
from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.config import DeepCodeConfig
from deepcode.src.modules.args_parser import DeepCodeArgsParser
from deepcode.src.modules.analyzer import DeepCodeAnalyzer
from deepcode.src.modules.http import DeepCodeHttp
# own extra utils and constants
from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS, CLI_ALIASES
from deepcode.src.constants.config_constants import DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST
from deepcode.src.utils.config_utils import handle_backend_host_last_slash


class DeepCodeLib:
    def __init__(self, isCliMode=False):
        if isCliMode:
            self.args_parser = DeepCodeArgsParser()

        # DI into config
        self.config = DeepCodeConfig(isCliMode)
        self.http = DeepCodeHttp(self.config)

        self.user = DeepCodeUser(self.http)
        self.analyzer = DeepCodeAnalyzer(self.http)

    def activate_cli(self):
        cli_args_dict = self.args_parser.parse()
        if (len(cli_args_dict)):
            self.process_cli_args(cli_args_dict)

    def process_cli_args(self, cli_args_dict):
        command = cli_args_dict[CLI_ARGS_NAMESPACE_NAME]
        [login, logout, analyze, config] = CLI_SUPPORTED_COMMANDS
        command_trigger = {
            login: lambda: self.cli_login_actions(),
            logout: lambda: self.cli_logout_actions(),
            config: lambda: self.cli_config_actions(cli_args_dict),
            analyze: lambda: self.cli_analyze_actions(cli_args_dict)
        }
        command_trigger[CLI_ALIASES[command]
                        if command in CLI_ALIASES.keys() else command]()

    # Handle cli config actions
    def cli_config_actions(self, cli_args_dict):
        [json_format, txt_format] = SUPPORTED_RESULTS_FORMATS
        chosen_format = cli_args_dict['format']
        if not chosen_format:
            print('You can configure backend host and change it for your own')
            new_backend_host = input(
                'Enter new backend host or leave blank for default({}): '.format(DEEPCODE_BACKEND_HOST))
            if new_backend_host:
                self.config.update_backend_host(
                    handle_backend_host_last_slash(new_backend_host))
                print('Backend host successfully updated')
            return
        if chosen_format == json_format:
            print(self.config.display_config_to_json())
        if chosen_format == txt_format:
            print(self.config.display_config_to_txt())

    # handle cli login actions
    def cli_login_actions(self):
        is_user_logged_in = self.config.is_user_logged_in()
        is_upload_confirmed = self.config.is_code_upload_confirmed()

        # if user is already logged in
        if is_user_logged_in:
            if not is_upload_confirmed:
                print('User is Already logged in, but code upload is not confirmed')
                confirm_response = self.user.confirm_code_upload()
                if confirm_response:
                    self.config.activate_code_upload()
            else:
                print('User is Already logged in')
            return

        # login user flow
        [token, login_url] = self.user.login().values()
        webbrowser.get().open_new(login_url)
        print('The deepCode login page {login_url} is opened in browser.\nWaiting for login...'.format(
            login_url))
        login_account_type = self.user.check_login(token)
        print('You are succesfully logged in')
        confirm_response = self.user.confirm_code_upload()
        self.config.set_user_login_config(
            token, login_account_type, confirm_response)

    # logout of user, just clean user config data
    def cli_logout_actions(self):
        self.config.delete_user_config()
        print('User has been logged out')

    def cli_analyze_actions(self, analyze_options):
        # check user login and confirm statuses
        is_user_logged_in = self.config.is_user_logged_in()
        is_upload_confirmed = self.config.is_code_upload_confirmed()
        if not is_user_logged_in:
            print('user is not logged in')
            return
        if not is_upload_confirmed:
            print('code upload is not confirmed')
            return

        # print(analyze_options)
        bundle_path = analyze_options['path']
        result_view_format = analyze_options['format']
        should_analyze_remote = analyze_options['remote']

        if should_analyze_remote:
            analysis_results = self.analyzer.analyze_repo(bundle_path)
            # TODO: results formats depending on format
        else:
            analysis_results = self.analyzer.analyze_files_bundle(bundle_path)
            # TODO: results format
        print(analysis_results)
