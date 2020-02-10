import asyncio
from .connection import api_call

ANALYSIS_PROGRESS_INTERVAL = 2
ANALYSIS_RETRY_DELAY = 2
ANALYSIS_RETRIES = 3

async def get_analysis(bundle_id, linters_enabled):

    success_statuses = ['DONE'] if linters_enabled else ['DONE', 'DC_DONE']
    attempt = 0

    while(True):
        path = ('analysis/{}?linters' if linters_enabled else 'analysis/{}').format(bundle_id)
        data = await api_call(path)
        
        if data.get('status') in success_statuses and data.get('analysisResults'):
            return data
        
        elif data['status'] == 'FAILED':
            if attempt >= ANALYSIS_RETRIES:
                raise RuntimeError("Analysis failed for {} times. It seems, Deepcode has some issues. Please contact Deepcode. Response --> {}".format(ANALYSIS_RETRIES, data))
            
            attempt += 1
            await asyncio.sleep(ANALYSIS_RETRY_DELAY)

        elif data.get('progress'):
            print('analysing {:2.2f}%'.format(data['progress'] * 100))
            await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)

        else:
            print('initialising...')
            await asyncio.sleep(ANALYSIS_PROGRESS_INTERVAL)
