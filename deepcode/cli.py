"""
Command line interface for Deepcode
"""

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
from .constants import (DEFAULT_SERVICE_URL, CONFIG_FILE_PATH, SERVICE_URL_ENV, API_KEY_ENV)
from .formatter import format_txt


def _save_config(service_url, api_key, config_file):
    data = {
        'service_url': service_url,
        'api_key': api_key,
    }
    data = {k:v for k,v in data.items() if v}

    with open(config_file, 'w') as cfg:
        cfg.write(json.dumps(data))

def _config_logging(log_file):
    if log_file:
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
            datefmt='%m-%d %H:%M',
            filename=os.path.expanduser(log_file),
            filemode='w')
    
    console = logging.StreamHandler()
    console.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)


@click.group()
@click.option('--service-url', '-s', 'service_url',
    default=lambda: os.environ.get(SERVICE_URL_ENV, ''), 
    help="Custom DeepCode service URL (default: {})".format(DEFAULT_SERVICE_URL))
@click.option('--api-key', '-a', 'api_key', 
    default=lambda: os.environ.get(API_KEY_ENV, ''), 
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
        os.environ[SERVICE_URL_ENV] = service_url

    api_key = ctx.obj.get('api_key', '')
    if api_key:
        os.environ[API_KEY_ENV] = api_key


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
@click.option('--with-linters', '-l', 'linters_enabled', is_flag=True, help="Enable linters")
@click.option('--log-file', '-log', 'log_file',
    type=click.Path(file_okay=True, dir_okay=False),
    help="Forward all debugging messages to a file")
@click.option('--result-text', '-txt', 'result_txt', is_flag=True, help="Present results in txt format")
@click.pass_context
@coro
async def analyze(ctx, linters_enabled, paths, remote_params, log_file, result_txt):
    """
    Analyzes your code using Deepcode AI engine. 
    """
    _config_logging(log_file)
    
    try:
        if paths: # Local folders are going to be analysed
            paths = [os.path.abspath(p) for p in paths]
            results = await analize_folders(paths=paths, linters_enabled=linters_enabled)
        else:
            # Deepcode server will fetch git repository and analize it
            results = await analize_git(linters_enabled=linters_enabled, **remote_params)

        # Present results in json or textual way
        print( format_txt(results) if result_txt else json.dumps(results, sort_keys=True, indent=2) )

    except aiohttp.client_exceptions.ClientResponseError as exc:
        if exc.status == 401:
            logger.error('Auth token seems to be missing or incorrect. Run \"deepcode login\"')
        else:
            logger.error(exc)

    
