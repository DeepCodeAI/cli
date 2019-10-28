from deepcode.src.constants.config_constants import DEEPCODE_BACKEND_HOST
from deepcode.src.helpers.terminal_view_decorations import text_decorations, text__with_colors

CLI_PARSER_HELP_MESSAGES = {
    'login_help': 'login to DeepCode CLI',
    'logout_help': 'Logout from DeepCOde CLI',
    'config_help': '''Configure or show CLI config.\n Optional avaliable arguments: [-f], [--format] - types [json, txt]''',
    'analyze_help': 'Analyze code. Usage: analyze [-r] [path] [-f, --format] [json, txt].'
}

CLI_MAIN_HELP_DESCRIPTION = '''
DeepCode CLI for analyzing code(add help text)

DeepCode CLI description

usage: deepcode [command] [command argument] [-option] [option_argument]

positional arguments:
login       Login to DeepCode CLI using GitHub or BitBucket account
logout      Logout from CLI
config (c)  Configure Deepcode CLI backend host. Without options will provide steps to configure CLI.
            shortcuts: c
            options: [-f], [--format] - specifies results display format, supported formats: [json, txt]
            example:
                deepcode config -f txt #will display cli config in txt foromat
analyze (a) Command to analyze code.
            shortcuts: a 
            required: [path] - should be provided to specify the path to analyze. 
                [path] can be absolute path to files directory,
                or path to git repo from GitHub/BitBucket account of logged in user, e.g.[git_username]/[git_repo_name]/[commit(optional)]
            options:
                [-r], [--remote] - specifies analysis of git repository. 
                    Must be provided before [path]. Without it [path] will be considered as files directory path
                [-f], [--format] - specifies results display format, supported formats: [json, txt]
            examples:
                deepcode analyze [path_to_files_dir] -f json  #will analyze specified path and display results in json
                deepcode analyze -r [git_username/git_repo_name] -f txt  #will analyze specified repo of logged in user and display results as readable text
optional arguments:
-h, --help            show this help message and exit
\n
'''

CONFIG_SETTINGS_MESSAGES = {
    'configure_backend_host':
    '''To configure an on-premise AI backend, enter backend host. To use the cloud AI backend ({deepcode_host}) leave blank: '''.format(
        deepcode_host=text_decorations['bold'](DEEPCODE_BACKEND_HOST)),
    'backend_host_success_update': lambda new_host:
    text__with_colors['green'](
        'Backend host for DeepCode CLI has been successfully updated\nNow {new_host} is used.'.format(new_host=new_host))
}

CONFRIM_UPLOAD_HELPERS = {
    'confirm': text__with_colors['blue']('To analyze code, confirm remote analysis by DeepCode. Confirm? (y/n): '),
    'success': text__with_colors['green']('Remote analysis is successfully confirmed.'),
    'fail': text__with_colors['red']('Remote analysis is not confirmed.')
}

LOGIN_HELPERS = {
    'url': lambda login_url:
    text__with_colors['blue']('The deepCode login page {} is opened in browser.\nWaiting for login...'.format(
        text_decorations['bold'](login_url))),
    'login_success': text__with_colors['green']('Login has been successfull'),
    'logout': text__with_colors['green']('Logout has been successfull'),
    'login_without_confirm': text__with_colors['red']('Already logged in, but remote analysis is not confirmed'),
    'already_login': text__with_colors['green']('Already logged in'),
    'not_logged_in': text__with_colors['red']('Not logged in'),
}

ANALYSIS_HELPERS = {
    'analyzing': text__with_colors['blue']('Analyzing...'),
    'json_view_results': text__with_colors['green']('Deepcode Analysis Results in json format:'),
    'txt_view_results': text__with_colors['green']('Deepcode Analysis Results in text fromat:'),
    'empty_results': text__with_colors['green']('Everything is fine. No issues found.')
}

BUNDLE_HELPERS = {
    'creating': text__with_colors['blue']('Creating bundle...'),
    'uploading': text__with_colors['blue']('Uploading bundle...'),
    'empty': text__with_colors['blue']('Bundle is empty, nothing to analyze')
}
