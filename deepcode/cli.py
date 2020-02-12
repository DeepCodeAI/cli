import click
import json
import asyncio
import aiohttp
import os.path
import logging
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

from . import analize_folders, analize_git
from .utils import logger, coro
from .auth import login as login_task
from .git_utils import parse_git_uri
from .connection import DEFAULT_SERVICE_URL
from .formatter import format_txt

CONFIG_FILE_PATH = '~/.deepcode.json'

def _save_config(service_url, api_key, config_file):
    data = {
        'service_url': service_url,
        'api_key': api_key,
    }
    data = {k:v for k,v in data.items() if v}

    with open(config_file, 'w') as cfg:
        cfg.write(json.dumps(data))


@click.group()
@click.option('--service-url', '-s', 'service_url',
    default=lambda: os.environ.get('DEEPCODE_SERVICE_URL', ''), 
    help="Custom DeepCode service URL (e.g. {})".format(DEFAULT_SERVICE_URL))
@click.option('--api-key', '-a', 'api_key', 
    default=lambda: os.environ.get('DEEPCODE_API_KEY', ''), 
    help="Deepcode API key")
@click.option(
    '--config-file', '-c',
    type=click.Path(dir_okay=False),
    default=CONFIG_FILE_PATH,
    help="Config file (default: {})".format(CONFIG_FILE_PATH)
)
@click.pass_context
def main(ctx, service_url, api_key, config_file):
    """
    A tool, that detects bugs and quality issues in JavaScript, TypeScript, Python and Java..
    It uses a mighty engine based on AI from Deepcode.
    """

    filename = os.path.expanduser(config_file)

    config_data = {}
    if (not service_url or not api_key) and os.path.exists(filename):
        with open(filename) as cfg:
            try:
                config_data = json.loads(cfg.read())
            except json.JSONDecodeError:
                logger.error('config file seems to be broken. Please run \"deepcode config\"')

    ctx.obj = {
        'service_url': service_url or config_data.get('service_url', ''),
        'api_key': api_key or config_data.get('api_key', ''),
        'config_file': filename
    }

    service_url = ctx.obj.get('service_url', '')
    if service_url:
        os.environ['DEEPCODE_SERVICE_URL'] = service_url

    api_key = ctx.obj.get('api_key', '')
    if api_key:
        os.environ['DEEPCODE_API_KEY'] = api_key


@main.command()
@click.pass_context
def config(ctx):
    """
    Store configuration values in a file.
    """
    
    service_url = click.prompt(
        "Please enter Deepcode Service URL (or leave it blank to use {})".format(DEFAULT_SERVICE_URL),
        default=ctx.obj.get('service_url', '')
    )

    api_key = click.prompt(
        "Please enter your API key",
        default=ctx.obj.get('api_key', '')
    )

    _save_config(service_url, api_key, ctx.obj['config_file'])


@main.command()
@click.pass_context
@coro
async def login(ctx):
    """
    Initiate a new login protocal.
    User will be forwarded to Deepcode website to complete the process.
    """
    
    service_url = ctx.obj.get('service_url', '')

    api_key = await login_task(service_url)

    _save_config(service_url, api_key, ctx.obj['config_file'])

    print('Login Successful! You API key \"{}\" is saved.'.format(api_key))


class GitURI(click.ParamType):
    name = 'Remote'

    def convert(self, value, param, ctx):
        data = parse_git_uri(value)
        if not data:
            self.fail(
                f'{value} is not a valid Git URI. (e.g. git@<platform>:<owner>/<repo>.git@<oid> or https://<platform>/<owner>/<repo>.git@<oid>)',
                param,
                ctx,
            )
        
        return data

@main.command()
@optgroup.group('Source location', 
    cls=RequiredMutuallyExclusiveOptionGroup,
    help='The configuration of repository location')
@optgroup.option("--path", "-p", "paths", 
    multiple=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    help="Path to folder to be processed. Multiple paths are allowed")
@optgroup.option("--git-uri", "-r", "remote_params",
    type=GitURI(),
    help="Git URI (e.g. git@<platform>:<owner>/<repo>.git@<oid> or https://<platform>/<owner>/<repo>.git@<oid>)",
)
@click.option('--linters', '-l', 'linters_enabled', is_flag=True, help="Enable linters")
@click.option('--logging', '-log', 'logging_level', default='error',
    type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
@click.option('--format', default='json',
    type=click.Choice(['txt', 'json'], case_sensitive=False))
@click.pass_context
@coro
async def analyze(ctx, linters_enabled, paths, remote_params, logging_level, format):
    """
    Analyzes your code using Deepcode AI engine. 
    """
    if logging_level:
        logging_levels = {
            'debug': logging.DEBUG, 
            'info': logging.INFO, 
            'warning': logging.WARNING, 
            'error': logging.ERROR, 
            'critical': logging.CRITICAL
        }
        logging.basicConfig(level=logging_levels[logging_level])

    try:
        if paths:
            paths = [os.path.abspath(p) for p in paths]
            results = await analize_folders(paths=paths, linters_enabled=linters_enabled)
        else:
            results = await analize_git(linters_enabled=linters_enabled, **remote_params)

        if format == 'txt':
            format_txt(results)
        else:
            print(results)
    except aiohttp.client_exceptions.ClientResponseError as exc:
        if exc.status == 401:
            logger.error('Auth token seems to be missing or incorrect. Run \"deepcode login\"')
        else:
            logger.error(exc)

    
