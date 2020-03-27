"""
A module dedicated to implementing an analysis protocol.
"""

import asyncio
import aiohttp
from tqdm import tqdm

from .connection import api_call
from .utils import logger
from .constants import (ANALYSIS_PROGRESS_INTERVAL, ANALYSIS_RETRY_DELAY, ANALYSIS_RETRIES)
from .severity import filter_severity

STATUS_MAPPING = {
    'DC_DONE': 'Linters running',
    'DONE': 'Completed analysis'
}

def _status_decription(status):
    return STATUS_MAPPING.get(status, status).lower().capitalize()


async def get_analysis(bundle_id, linters_enabled=False, severity=1):
    """ Initiate analysis via API and wait for results. """

    success_statuses = ['DONE'] if linters_enabled else ['DONE', 'DC_DONE']
    attempt = 0

    path = {
        True: 'analysis/{}?severity={}&linters',
        False: 'analysis/{}?severity={}'
    }[linters_enabled].format(bundle_id, severity)

    with tqdm(total=100, unit='%', leave=False) as pbar:

        current_percentage = 0

        while(True):

            data = await api_call(path)

            pbar.set_description(
                _status_decription(data.get('status', ''))
                )

            if data.get('status') in success_statuses and data.get('analysisResults'):

                return {
                    'id': bundle_id,
                    'url': data['analysisURL'],
                    'results': filter_severity(data['analysisResults'], severity)
                }

            elif data['status'] == 'FAILED':
                if attempt >= ANALYSIS_RETRIES:
                    raise RuntimeError("Analysis failed for {} times. It seems, Deepcode has some issues. Please contact Deepcode. Response --> {}".format(ANALYSIS_RETRIES, data))

                logger.warning('Analysis failed. Retrying in {} sec'.format(ANALYSIS_RETRY_DELAY))
                attempt += 1
                await asyncio.sleep(ANALYSIS_RETRY_DELAY)

            elif data.get('progress'):

                progress = int(data['progress'] * 100)
                pbar.update(progress - current_percentage)
                current_percentage = progress

                await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)

            else:
                await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)
