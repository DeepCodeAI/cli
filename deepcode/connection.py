from urllib.parse import urljoin
import aiohttp
import zlib
from json import dumps

# API_TOKEN = '1eea7e6a02f82252a71732401eb2f6b3711f2db306e0bf88c3e50fd2b640fe79'
API_TOKEN = 'd9f5eb73e28d31bdc65d3eed3df165b16ac078477d0fa4749db2e8a5df5d499f'
#SERVICE_URL = 'https://www.deepcode.ai/publicapi/'
SERVICE_URL = 'http://localhost:8080/publicapi/'

async def api_call(path, method='GET', data=None, extra_headers={}, callback=lambda resp: resp.json()):
    url = urljoin(SERVICE_URL, path)
    
    default_headers = {
        'Session-Token': API_TOKEN,
        }
    
    if data:
        # Expect json string here
        data = dumps(data).encode('utf-8')
        data = zlib.compress(data, 9) if data else None

        default_headers.update({
            'Content-Type': 'application/json',
            'Content-Encoding': 'deflate'
        })
    
    # async def on_request_start(session, trace_config_ctx, params):
    #     print("Starting request")

    # async def on_request_end(session, trace_config_ctx, params):
    #     print("Ending request")

    async with aiohttp.request(
        url=url, method=method, 
        data=data, 
        headers=dict(default_headers, **extra_headers), 
        compress=None
        ) as resp:
        
        # content = await resp.text()
        #print('request succeeded with response --> ', content)
        #print('!'*80)
        return await callback(resp)
