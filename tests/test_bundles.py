#import httpretty
import asyncio
import pytest
from aiohttp import web
import aiohttp

from deepcode.bundle import get_filters, generate_bundle, create_git_bundle

API_KEY = '3f0c8e2f05b1465de310e4d7b3d80db7ee87bcf73225b6b3db97848b1d17784c'


@pytest.mark.asyncio
async def test_filters(aiohttp_client, loop):
    # httpretty.register_uri(
    #     httpretty.GET,
    #     "https://www.deepcode.ai/publicapi/filters",
    #     body=
    # )

    # Try to call without api key
    with pytest.raises(aiohttp.client_exceptions.ClientResponseError):
        await get_filters()
    
    filter_func = await get_filters(api_key=API_KEY)
    
    assert filter_func('sample_repository/utf8.js') == True


def test_generate_bundle():
    """ Test generating bundles """
    pass