import click
import asyncio
import aiohttp
import os.path
import logging
from click_option_group import optgroup, RequiredMutuallyExclusiveOptionGroup

from . import analize_folders, analize_git
from .utils import logger
from .git_utils import parse_git_uri

format_txt = lambda r: print(r)

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


@click.command()
@optgroup.group('Source location', 
    cls=RequiredMutuallyExclusiveOptionGroup,
    help='The configuration of repository location')
@optgroup.option("--path", "-p", "paths", 
    multiple=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True),
    help="Path to folder to be processed.")
@optgroup.option("--git-uri", "-r", "remote_params",
    type=GitURI(),
    help="Git URI (e.g. git@<platform>:<owner>/<repo>.git@<oid> or https://<platform>/<owner>/<repo>.git@<oid>)",
)
@optgroup.group('Environment configuration', help='The configuration of environment')
@optgroup.option('--linters', is_flag=True, help="Enable linters")
@optgroup.option('--service-url', help="Custom DeepCode service URL (e.g. https://www.deepcode.ai)")
@click.option('--logging', '-l', 'logging_level', default='error',
    type=click.Choice(['debug', 'info', 'warning', 'error', 'critical'], case_sensitive=False))
@click.option('--format', default='json',
    type=click.Choice(['txt', 'json'], case_sensitive=False))
def process(linters, service_url, paths, remote_params, logging_level, format):
    # TODO: support multiple paths 
    if service_url:
        os.environ['SERVICE_URL'] = service_url

    if logging_level:
        logging_levels = {
            'debug': logging.DEBUG, 
            'info': logging.INFO, 
            'warning': logging.WARNING, 
            'error': logging.ERROR, 
            'critical': logging.CRITICAL
        }
        logging.basicConfig(level=logging_levels[logging_level])

    async def runner(func, *args, **kwargs):
        try:
            results = await func(*args, **kwargs)

            if format == 'txt':
                format_txt(results)
            else:
                print(results)
        except aiohttp.client_exceptions.ClientResponseError as exc:
            if exc.status == 401:
                logger.error('Auth token seems to be missing or incorrect')
            else:
                logger.error(exc)

    if paths:
        paths = [os.path.abspath(p) for p in paths]
        task = runner(analize_folders, paths=paths, linters_enabled=linters)
    else:
        task = runner(analize_git, linters_enabled=linters, **remote_params)

    loop = asyncio.get_event_loop()
    loop.run_until_complete(task)
