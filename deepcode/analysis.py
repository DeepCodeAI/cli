import asyncio
import aiohttp

from .connection import api_call
from .utils import profile_speed, logger

ANALYSIS_PROGRESS_INTERVAL = 2
ANALYSIS_RETRY_DELAY = 5
ANALYSIS_RETRIES = 3

@profile_speed
async def get_analysis(bundle_id, linters_enabled):
    """ Initiate analysis via API and wait for results. """

    success_statuses = ['DONE'] if linters_enabled else ['DONE', 'DC_DONE']
    attempt = 0

    while(True):
        path = ('analysis/{}?linters' if linters_enabled else 'analysis/{}').format(bundle_id)
        data = await api_call(path)
        
        if data.get('status') in success_statuses and data.get('analysisResults'):
            return {
                'id': bundle_id,
                'url': data['analysisURL'],
                'results': data['analysisResults']
            }
        
        elif data['status'] == 'FAILED':
            if attempt >= ANALYSIS_RETRIES:
                raise RuntimeError("Analysis failed for {} times. It seems, Deepcode has some issues. Please contact Deepcode. Response --> {}".format(ANALYSIS_RETRIES, data))
            
            logger.info('Analysis failed. Retrying in {} sec'.format(ANALYSIS_RETRY_DELAY))
            attempt += 1
            await asyncio.sleep(ANALYSIS_RETRY_DELAY)

        elif data.get('progress'):
            logger.info('{} {:2.0f}%'.format(data.get('status', '').lower(), data['progress'] * 100))
            await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)

        else:
            logger.info('initialising...')
            await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)
