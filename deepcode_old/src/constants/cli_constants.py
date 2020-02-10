CLI_NAME = 'deepcode',
CLI_ARGS_NAMESPACE_NAME = 'cli_commands'
CLI_SUPPORTED_COMMANDS = ['login', 'logout', 'analyze', 'config']
CLI_ALIASES = {
    'c': 'config',
    'a': 'analyze'
}
CLI_SUPPORTED_OPTIONS = [
    ['path'],
    ['-r', '--remote'],
    ['-f', '--format'],
    ['-s', '--silent'],
    ['-v', '--version']
]
SUPPORTED_RESULTS_FORMATS = ['json', 'txt']
MAX_PROGRESS_VALUE = 100
