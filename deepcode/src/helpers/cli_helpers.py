from deepcode.src.constants.config_constants import DEEPCODE_BACKEND_HOST
from deepcode.src.helpers.terminal_view_decorations import text_decorations, text__with_colors

CLI_PARSER_HELP_MESSAGES = {
    'login_help': 'login to DeepCode CLI',
    'logout_help': 'Logout from DeepCOde CLI',
    'config_help': '''Configure or show CLI config.\n Optional avaliable arguments: [-f], [--format] - types [json, txt]''',
    'analyze_help': 'Analyze code. Usage: analyze [-r] [path] [-f, --format] [json, txt].'
}

CLI_MAIN_HELP_DESCRIPTION = '''
DeepCode CLI for analyzing code

DeepCode's AI algorithms continuously learn from bugs and issues fixed on open source
repos. CLI will analyze your code and infrom you about critical vulnerabilities you need to solve
in your code. Don't let security bugs go to production. Save time
finding and fixing them.

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
            required: 
                [path]  - path to analyze bundle
                [base_path] [target_path] - paths to perform diff analysis of two bundles 
                paths can be absolute path to files directory or paths to git repo from GitHub/BitBucket account of logged in user,
                 e.g. owner/repo_name/commit(optional)
            options:
                [-r], [--remote] - specifies analysis of git repository. 
                    Must be provided before [path]. Without it [path] will be considered as files directory path
                [-f], [--format] - specifies results display format, supported formats: [json, txt]. If not specified, default format is txt
            examples:
                deepcode analyze [path_to_files_dir] -f json  #will analyze specified path and display results in json
                deepcode a -r [git_username/git_repo_name] -f txt  #will analyze specified repo of logged in user and display results as readable text
                deepcode a [base_path_to_files] [target_path_to_files] -f json #will perform diff analysis of two bundles and display results in json
                deepcode a -r [owner/repo/commit] [owner/repo/commit] -f txt #will perform diff analysis of two remote bundles and display results in text
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
    'txt_view_results': text__with_colors['green']('Deepcode Analysis Results in text format:'),
    'empty_results': text__with_colors['green']('Everything is fine. No issues found.')
}

BUNDLE_HELPERS = {
    'creating': lambda path='': text__with_colors['blue']('Creating {} bundle...'.format(path)),
    'uploading': lambda path='': text__with_colors['blue']('Uploading {} bundle...'.format(path)),
    'empty': lambda path='': text__with_colors['blue']('Bundle {} is empty, nothing to analyze.'.format(path)),
    'creating_diff': 'Creating bundles...'
}
