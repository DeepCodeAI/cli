"""
A module dedicated to authenticating users via Deepcode website
"""

import asyncio
import webbrowser
import aiohttp

from .utils import logger
from .connection import api_call, SOURCE
from .constants import AUTH_POLLING_INTERVAL


async def login(service_url):
    """
    Initiate a new login protocol.
    User will be forwarded to Deepcode website to complete the process.
    """
    res = await api_call('login', method="POST", data={'source': SOURCE})
    api_key, login_url = res['sessionToken'], res['loginURL']

    # Open browser to complete authentication and assign api_key and user
    webbrowser.get().open_new(login_url)

    while(True):
        try:
            await asyncio.sleep(AUTH_POLLING_INTERVAL)
            status = await api_call('session', method="GET", 
                callback=asyncio.coroutine(lambda r: r.status), 
                api_key=api_key)
            if status == 304:
                print('Please, complete login process in opened browser. Re-checking session in {} sec'.format(AUTH_POLLING_INTERVAL))
                continue
            else:
                # it means success, when we got 200 status code
                return api_key
        except aiohttp.client_exceptions.ClientResponseError:
            logger.error('Missing or invalid sessionToken')
            raise
