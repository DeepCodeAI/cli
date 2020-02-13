from urllib.parse import urljoin
import aiohttp
import asyncio
import zlib
import os
from json import dumps
from functools import wraps
import inspect

from .utils import logger

# API_KEY = '1eea7e6a02f82252a71732401eb2f6b3711f2db306e0bf88c3e50fd2b640fe79'
# API_KEY = 'd9f5eb73e28d31bdc65d3eed3df165b16ac078477d0fa4749db2e8a5df5d499f' # localhost

DEFAULT_SERVICE_URL = 'https://www.deepcode.ai'
NETWORK_RETRY_DELAY = 5
SOURCE = 'CLI'

# BACKEND_STATUS_CODES = {
#     'success': 200,
#     'login_in_progress': 304,
#     'token': 401,
#     'invalid_content': 400,
#     'invalid_bundle_access': 403,
#     'expired_bundle': 404,
#     'large_payload': 413
# }

def reconnect(func):
  
    @wraps(func)
    async def wrapper(*args, **kwargs):
        while(True):
            try:
                return await func(*args, **kwargs)
            except aiohttp.client_exceptions.ClientConnectionError:
                logger.warning("Server is not available. Retrying in {} seconds".format(NETWORK_RETRY_DELAY))
                # In case of network disruptions, we just retry without affecting any logic
                await asyncio.sleep(NETWORK_RETRY_DELAY)
            except aiohttp.client_exceptions.ClientResponseError as exc:
                if exc.status == 500:
                    logger.warning("Server gives 500. Retrying in {} seconds".format(NETWORK_RETRY_DELAY))
                    # In case of temporary server failures, we just retry without affecting any logic
                    await asyncio.sleep(NETWORK_RETRY_DELAY)
                else:
                    raise

    return wrapper
    

@reconnect
async def api_call(path, method='GET', data=None, extra_headers={}, callback=lambda resp: resp.json(), compression_level=6, api_key=''):
    SERVICE_URL = os.environ.get('DEEPCODE_SERVICE_URL', '') or DEFAULT_SERVICE_URL
    API_KEY = api_key or os.environ.get('DEEPCODE_API_KEY', '')

    url = urljoin(urljoin(SERVICE_URL, '/publicapi/'), path)
    
    default_headers = {
        'Session-Token': API_KEY,
        }
    
    if data:
        # Expect json string here
        data = dumps(data).encode('utf-8')
        data = zlib.compress(data, level=compression_level)

        default_headers.update({
            'Content-Type': 'application/json',
            'Content-Encoding': 'deflate'
        })
    
    # async def on_request_start(session, trace_config_ctx, params):
    #     logger.debug("Starting request")

    # async def on_request_end(session, trace_config_ctx, params):
    #     logger.debug("Ending request")

    async with aiohttp.request(
        url=url, method=method, 
        data=data, 
        raise_for_status=True,
        headers=dict(default_headers, **extra_headers), 
        compress=None
        ) as resp:
        
        # logger.debug('status --> {}'.format(resp.status))
        # content = await resp.text()
        
        return await callback(resp)
        