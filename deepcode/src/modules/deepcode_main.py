
import json
import webbrowser

from deepcode.src.modules.user import DeepCodeUser
from deepcode.src.modules.config import DeepCodeConfig
from deepcode.src.modules.args_parser import DeepCodeArgsParser
from deepcode.src.modules.analyzer import DeepCodeAnalyzer
from deepcode.src.modules.http import DeepCodeHttp
from deepcode.src.modules.errors_handler import ErrorHandler

from deepcode.src.constants.cli_constants \
    import CLI_ARGS_NAMESPACE_NAME, CLI_SUPPORTED_COMMANDS, SUPPORTED_RESULTS_FORMATS, CLI_ALIASES
from deepcode.src.constants.config_constants import DEEPCODE_CONFIG_NAMES, DEEPCODE_BACKEND_HOST, CURRENT_FOLDER_PATH
from deepcode.src.helpers.cli_helpers import LOGIN_HELPERS, ANALYSIS_HELPERS, BUNDLE_HELPERS
from deepcode.src.helpers.errors_messages import BACKEND_ERRORS


class DeepCodeMainModule:
    def __init__(self, is_cli_mode=False):
        self.is_cli_mode = is_cli_mode
        if self.is_cli_mode:
            self.args_parser = DeepCodeArgsParser()

        self.config = DeepCodeConfig()
        self.http = DeepCodeHttp(self.config)
        self.user = DeepCodeUser(self.http)
        self.analyzer = DeepCodeAnalyzer(self.http)
        ErrorHandler.set_mode_for_handling_errors(
            self.is_cli_mode, self.config)

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

    # handle cli config command
    def cli_config_actions(self, cli_args_dict):
        [json_format, txt_format] = SUPPORTED_RESULTS_FORMATS
        chosen_format = cli_args_dict['format']
        if not chosen_format:
            return self.config.configure_cli()
        if chosen_format == json_format:
            print(self.config.display_config_to_json())
        if chosen_format == txt_format:
            print(self.config.display_config_to_txt())

    # handle cli login command
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

    # confirm uploading code
    def confirm_upload_common_actions(self):
        confirm_response = self.user.confirm_code_upload()
        if confirm_response:
            self.config.activate_code_upload()

    # logout of user (cleans up user config data)
    def cli_logout_actions(self):
        self.config.delete_user_config()
        print(LOGIN_HELPERS['logout'])

    # handle analyze command
    def cli_analyze_actions(self, analyze_options):
        analyze_func_to_call = self.cli_pre_analyze_actions(analyze_options)
        if not analyze_func_to_call:
            return
        analysis_results = analyze_func_to_call()
        self.cli_analysis_display_actions(analysis_results, analyze_options)

    def cli_pre_analyze_actions(self, analyze_options):
        is_user_logged_in, is_upload_confirmed = self.config.check_login_and_confirm()
        if not is_user_logged_in:
            print(LOGIN_HELPERS['not_logged_in'])
            return
        if not is_upload_confirmed:
            print(LOGIN_HELPERS['login_without_confirm'])
            self.confirm_upload_common_actions()
            return
        single_path, two_paths = (1, 2)
        paths = analyze_options['path']
        paths_count = len(paths)
        if len(paths) > two_paths:
            self.args_parser.show_help_for_many_bundles()
            return
        if len(paths) == single_path:
            return lambda: self.analyze_main_actions(analyze_options['path'][0], analyze_options)
        if len(paths) == two_paths:
            return lambda: self.analyze_main_actions(analyze_options['path'], analyze_options, is_diff_analysis=True)

    def analyze_main_actions(self, bundle_path, analyze_options, is_diff_analysis=False):
        analyze_func = lambda *args, **kwargs: None
        should_analyze_remote = analyze_options['remote']
        show_progressbar = not analyze_options['silent']
        if should_analyze_remote:
            analyze_func = self.analyzer.analyze_diff_repos if is_diff_analysis else self.analyzer.analyze_repo
        else:
            analyze_func = self.analyzer.diff_analyze_files_bundles if is_diff_analysis else self.analyzer.analyze_files_bundle
        analysis_results = analyze_func(
            bundle_path, show_progressbar=show_progressbar)
        return analysis_results

    # handle cli results view depending on selected options
    def cli_analysis_display_actions(self, analysis_results, analyze_options):
        if not analysis_results or not len(analysis_results):
            print(ANALYSIS_HELPERS['empty_results'])
            return
        if analysis_results == BUNDLE_HELPERS['empty']:
            print(BUNDLE_HELPERS['empty'])
            return
        result_view_format = analyze_options['format']
        should_analyze_remote = analyze_options['remote']
        json_format, txt_format = SUPPORTED_RESULTS_FORMATS
        if not result_view_format or result_view_format == txt_format:
            display_view = (
                ANALYSIS_HELPERS['txt_view_results'],
                self.analyzer.display_analysis_results_in_txt(
                    analysis_results, is_repo=should_analyze_remote)
            )
        if result_view_format == json_format:
            display_view = (
                ANALYSIS_HELPERS['json_view_results'],
                self.analyzer.analysis_results_in_json(analysis_results)
            )
        print(*display_view, sep='\n')

    # analyze func for module mode
    @ErrorHandler.module_mode_error_decorator
    def module_analyze_actions(self, paths, is_repo=False):
        is_user_logged_in, is_upload_confirmed = self.config.check_login_and_confirm()
        if not is_user_logged_in:
            ErrorHandler.raise_backend_error('token')

        parent_path, child_path = paths.values()
        is_diff_analysis = bool(child_path)
        path_to_analyze = [
            parent_path, child_path] if is_diff_analysis else parent_path or CURRENT_FOLDER_PATH
        analysis_options = {
            'remote': is_repo,
            'silent': True
        }
        analysis_results = self.analyze_main_actions(
            path_to_analyze,
            analysis_options,
            is_diff_analysis=is_diff_analysis
        )
        return json.dumps(analysis_results)
