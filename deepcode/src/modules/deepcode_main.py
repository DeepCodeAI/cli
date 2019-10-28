# python modules
import json
import webbrowser
# own modules
from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.config import DeepCodeConfig
from deepcode.src.modules.args_parser import DeepCodeArgsParser
from deepcode.src.modules.analyzer import DeepCodeAnalyzer
from deepcode.src.modules.http import DeepCodeHttp
from deepcode.src.modules.errors_handler import DeepCodeErrors
# own extra utils and constants
from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS, CLI_ALIASES
from deepcode.src.constants.config_constants import DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST, CURRENT_FOLDER_PATH
from deepcode.src.utils.config_utils import handle_backend_host_last_slash
from deepcode.src.helpers.cli_helpers import CONFIG_SETTINGS_MESSAGES, LOGIN_HELPERS, ANALYSIS_HELPERS, BUNDLE_HELPERS
from deepcode.src.helpers.errors_messages import BACKEND_ERRORS


class DeepCodeMainModule:
    def __init__(self, is_cli_mode=False):
        self.is_cli_mode = is_cli_mode
        if self.is_cli_mode:
            self.args_parser = DeepCodeArgsParser()

        DeepCodeErrors.set_mode_for_handling_errors(self.is_cli_mode)

        self.config = DeepCodeConfig()
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
            new_backend_host = input(
                CONFIG_SETTINGS_MESSAGES['configure_backend_host'])
            if not new_backend_host and not self.config.is_current_backend_host_is_default():
                new_backend_host = DEEPCODE_BACKEND_HOST
            if new_backend_host:
                processed_host = handle_backend_host_last_slash(
                    new_backend_host)
                self.config.update_backend_host(processed_host)
                print(CONFIG_SETTINGS_MESSAGES['backend_host_success_update'](
                    processed_host))
            return
        if chosen_format == json_format:
            print(self.config.display_config_to_json())
        if chosen_format == txt_format:
            print(self.config.display_config_to_txt())

    # handle cli login actions
    def cli_login_actions(self):
        is_user_logged_in, is_upload_confirmed = self.config.check_login_and_confirm()

        # if user is already logged in
        if is_user_logged_in:
            if not is_upload_confirmed:
                print(LOGIN_HELPERS['login_without_confirm'])
                self.confirm_upload_common_actions()
            else:
                print(LOGIN_HELPERS['already_login'])
            return

        # login user flow
        logged_in = self.user.login()
        [token, login_url] = logged_in.values()
        webbrowser.get().open_new(login_url)
        print(LOGIN_HELPERS['url'](login_url))
        login_account_type = self.user.check_login(token)
        print(LOGIN_HELPERS['login_success'])
        confirm_response = self.user.confirm_code_upload()
        self.config.set_user_login_config(
            token, login_account_type, confirm_response)

    def confirm_upload_common_actions(self):
        confirm_response = self.user.confirm_code_upload()
        if confirm_response:
            self.config.activate_code_upload()

    # logout of user, just clean user config data
    def cli_logout_actions(self):
        self.config.delete_user_config()
        print(LOGIN_HELPERS['logout'])

    def cli_analyze_actions(self, analyze_options):
        # check user login and confirm statuses
        # TESTS,
        # bundle_paths = analyze_options['path']
        # max_paths_count = 2
        # if not len(bundle_paths) or len(bundle_paths) > max_paths_count:
        #     self.args_parser.show_help_on_error()
        #     return
        is_user_logged_in, is_upload_confirmed = self.config.check_login_and_confirm()
        if not is_user_logged_in:
            print(LOGIN_HELPERS['not_logged_in'])
            return LOGIN_HELPERS['not_logged_in']
        if not is_upload_confirmed:
            print(LOGIN_HELPERS['login_without_confirm'])
            self.confirm_upload_common_actions()
            return LOGIN_HELPERS['login_without_confirm']

        # if len(bundle_paths) == max_paths_count:
        #     bundle_path_one, bundle_path_two = bundle_paths
        # if len(bundle_paths) == 1:
        #     bundle_path = bundle_paths
        bundle_path = analyze_options['path']

        should_analyze_remote = analyze_options['remote']

        analysis_results = self.analyze_common_actions(
            bundle_path, is_remote=should_analyze_remote)

        if not analysis_results or not len(analysis_results):
            print(ANALYSIS_HELPERS['empty_results'])
            return
        if analysis_results == BUNDLE_HELPERS['empty']:
            print(BUNDLE_HELPERS['empty'])
            return
        result_view_format = analyze_options['format']
        json_format, txt_format = SUPPORTED_RESULTS_FORMATS
        if not result_view_format or result_view_format == txt_format:
            print(ANALYSIS_HELPERS['txt_view_results'])
            print(self.analyzer.display_analysis_results_in_txt(
                analysis_results, is_repo=should_analyze_remote))
        if result_view_format == json_format:
            print(ANALYSIS_HELPERS['json_view_results'])
            print(self.analyzer.analysis_results_in_json(analysis_results))

    def analyze_common_actions(self, bundle_path, is_remote=False):
        if is_remote:
            analysis_results = self.analyzer.analyze_repo(
                bundle_path, is_cli_mode=self.is_cli_mode)
        else:
            analysis_results = self.analyzer.analyze_files_bundle(
                bundle_path, is_cli_mode=self.is_cli_mode)
        return analysis_results

    @DeepCodeErrors.backend_error_decorator
    def module_analyze_actions(self, path, is_repo):
        is_user_logged_in, is_upload_confirmed = self.config.check_login_and_confirm()
        if not is_user_logged_in:
            DeepCodeErrors.raise_backend_error('token')
        analysis_results = self.analyze_common_actions(
            path or CURRENT_FOLDER_PATH, is_remote=is_repo or False)
        return json.dumps(analysis_results)
