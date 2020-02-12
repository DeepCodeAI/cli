import asyncio

from .connection import api_call, SOURCE

async def login(service_url):
    """
    Initiate a new login protocal.
    User will be forwarded to Deepcode website to complete the process.
    """
    res = await api_call('login', method="POST", data={'source': SOURCE})
    api_key, login_url = res['sessionToken'], res['loginURL']

    
