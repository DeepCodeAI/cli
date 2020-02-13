import asyncio
import aiohttp
from tqdm import tqdm

from .connection import api_call
from .utils import logger

ANALYSIS_PROGRESS_INTERVAL = 2
ANALYSIS_RETRY_DELAY = 5
ANALYSIS_RETRIES = 3

STATUS_MAPPING = {
    'DC_DONE': 'Linters running',
    'DONE': 'Completed analysis'
}

def _status_decription(status):
    return STATUS_MAPPING.get(status, status).lower().capitalize()


async def get_analysis(bundle_id, linters_enabled):
    """ Initiate analysis via API and wait for results. """

    success_statuses = ['DONE'] if linters_enabled else ['DONE', 'DC_DONE']
    attempt = 0

    with tqdm(total=100, unit='%', leave=False) as pbar:

        current_percentage = 0
        while(True):
            path = ('analysis/{}?linters' if linters_enabled else 'analysis/{}').format(bundle_id)
            data = await api_call(path)

            pbar.set_description(
                _status_decription(data.get('status', ''))
                )
            
            if data.get('status') in success_statuses and data.get('analysisResults'):
                return {
                    'id': bundle_id,
                    'url': data['analysisURL'],
                    'results': data['analysisResults']
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
