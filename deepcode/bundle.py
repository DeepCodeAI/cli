"""
A module dedicated to implementing an bundle protocol.
"""

import os
import json
import asyncio
import time
from funcy import chunks
from tqdm import tqdm
from functools import partial

from .connection import api_call
from .files import get_file_content, compose_file_buckets, prepare_file_path
from .utils import logger
from .constants import MAX_BUCKET_SIZE


async def get_filters(api_key=''):
    """ Fetch supported file extensions """
    filters = await api_call('filters', api_key=api_key)
    logger.debug('allowed files: {}'.format(filters))
    supported_extensions, expected_config_files = set(filters['extensions']), set(filters['configFiles'])
    return lambda n: os.path.splitext(n)[-1] in supported_extensions or n in expected_config_files


async def _request_file_bundle(path, method, file_hashes, api_key):

    files = {prepare_file_path(p): h for p, h in file_hashes}

    res = await api_call(
        path='bundle', method='POST', 
        data={'files': files, 'removedFiles': []}, 
        compression_level=9,
        api_key=api_key)

    bundle_id, missing_files = res['bundleId'], res['missingFiles']
    logger.debug('bundle id: {} | missing_files: {}'.format(bundle_id, len(missing_files)))
    return bundle_id, missing_files


def extend_file_bundle(bundle_id):
    """ Extend bundle via API  """
    return 


async def generate_bundle(file_hashes, api_key=''):
    """ Generate bundles via API. Incapsulates all logic of our bundle protocol. """

    async def _complete_bundle(bundle_func, api_key):
        bundle_id, missing_files = await bundle_func(api_key=api_key)
        while(missing_files):
            await fulfill_bundle(bundle_id, missing_files, api_key) # Send all missing files
            missing_files = await check_bundle(bundle_id, api_key) # Check that all files are uploaded
        
        return bundle_id

    bundle_id = None
    
    with tqdm(total=len(file_hashes), desc='Generated bundles', unit='bundle', leave=False) as pbar:

        for chunked_files in chunks(int(MAX_BUCKET_SIZE // 200), file_hashes):

            if not bundle_id:
                bundle_func = partial(_request_file_bundle, path='bundle', method='POST', file_hashes=file_hashes)
            else:
                bundle_func = partial(_request_file_bundle, path='bundle/{}'.format(bundle_id), method='PUT', file_hashes=file_hashes)

            bundle_id = await _complete_bundle( bundle_func, api_key)
            pbar.update(len(chunked_files))
            
        return bundle_id
        

async def create_git_bundle(platform, owner, repo, oid):
    """ Create a git bundle via API  """
    data = {
        'platform': platform, 
        'owner': owner, 
        'repo': repo
    }

    if oid:
        data['oid'] = oid
    
    res = await api_call('bundle', method='POST', data=data, compression_level=9)
    return res['bundleId']


async def check_bundle(bundle_id, api_key=''):
    """ Check missing files in bundle via API """
    data = await api_call('bundle/{}'.format(bundle_id), method='GET', api_key=api_key)
    return data['missingFiles']


async def upload_bundle_files(bundle_id, entries, api_key):
    """
    Each entry should contain of: (path, hash)
    """
    
    data = []
    for file_path, file_hash in entries:
        file_content = get_file_content(file_path)
        data.append({
            'fileHash': file_hash, 
            'fileContent': file_content 
        })
    
    await api_call(
        'file/{}'.format(bundle_id), 
        method='POST', 
        data=data, 
        callback=lambda resp: resp.text(),
        api_key=api_key
        )


async def fulfill_bundle(bundle_id, missing_files, api_key=''):
    """ Upload missing files to bundle via API """
    if not missing_files:
        return
    logger.debug('Uploading {} missing files'.format(len(missing_files)))
    with tqdm(total=len(missing_files), desc='Uploading missing files', unit='files', leave=False) as pbar:

        async def _wrap(chunk):
            await upload_bundle_files(bundle_id, chunk, api_key)
            pbar.update(len(chunk))

        tasks = [
            _wrap(chunk)
            for chunk in compose_file_buckets(missing_files)
        ]
        if tasks:
            await asyncio.wait(tasks)
        else:
            logger.debug('No new files sent, as all files have been uploaded earlier')
