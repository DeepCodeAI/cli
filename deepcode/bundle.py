import os
import json
import asyncio
import time

from .connection import api_call
from .files import get_file_content, compose_file_buckets

async def get_filters():
    filters = await api_call('filters')
    # print('filters --> ', filters)
    return filters

async def create_bundle(file_hashes):
    data = await api_call('bundle', method='POST', data={'files': file_hashes})
    return data['bundleId'], data['missingFiles']


async def check_bundle(bundle_id):
    data = await api_call('bundle/{}'.format(bundle_id), method='GET')
    return data['missingFiles']


async def upload_bundle_files(bundle_id, entries, index):
    """
    Each entry should contain of: (path, hash, size)
    """
    start_time = time.time()
    
    data = []
    for file_path, file_hash, file_size in entries:
        file_content = get_file_content(file_path)
        data.append({
            'fileHash': file_hash, 
            'fileContent': file_content 
        })
    
    await api_call(
        'file/{}'.format(bundle_id), 
        method='POST', 
        data=data, 
        callback=lambda resp: resp.text()
        )

    print('#{:2.0f} in {:10.2f} sec | sent {} files with size: {}'.format(index, time.time() - start_time, len(entries), sum([e[2] for e in entries])))


async def fulfill_bundle(bundle_id, missing_files):
    
    if not missing_files:
        return
    
    tasks = [
        upload_bundle_files(bundle_id, chunk, index)
        for index, chunk in enumerate(compose_file_buckets(missing_files))
    ]
    if tasks:
        await asyncio.gather(*tasks)
    else:
        print('No new files sent, as all files have been uploaded earlier')
