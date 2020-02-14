"""
A module dedicated to communication with Deepcode API.
"""
from urllib.parse import urljoin
import aiohttp
import asyncio
import zlib
import os
from json import dumps
from functools import wraps

from .utils import logger
from .constants import (DEFAULT_SERVICE_URL, NETWORK_RETRY_DELAY, SOURCE, SERVICE_URL_ENV, API_KEY_ENV)

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
    SERVICE_URL = os.environ.get(SERVICE_URL_ENV, '') or DEFAULT_SERVICE_URL
    API_KEY = api_key or os.environ.get(API_KEY_ENV, '')

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
        