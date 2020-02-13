"""
A module dedicated to implementing an bundle protocol.
"""

import os
import json
import asyncio
import time
from funcy import chunks
from tqdm import tqdm

from .connection import api_call
from .files import get_file_content, compose_file_buckets
from .utils import logger
from .constants import MAX_BUCKET_SIZE


async def get_filters():
    """ Fetch supported file extensions """
    filters = await api_call('filters')
    logger.debug('allowed files: {}'.format(filters))
    supported_extensions, expected_config_files = set(filters['extensions']), set(filters['configFiles'])
    return lambda n: os.path.splitext(n)[-1] in supported_extensions or n in expected_config_files


async def _request_file_bundle(path, method, file_hashes):

    res = await api_call(
        path='bundle', method='POST', 
        data={'files': dict(file_hashes), 'removedFiles': []}, 
        compression_level=9)

    bundle_id, missing_files = res['bundleId'], res['missingFiles']
    logger.debug('bundle id: {} | missing_files: {}'.format(bundle_id, len(missing_files)))
    return bundle_id, missing_files


def create_file_bundle(file_hashes):
    """ Create a new bundle via API  """
    return _request_file_bundle('bundle', 'POST', file_hashes)


def extend_file_bundle(bundle_id, file_hashes):
    """ Extend bundle via API  """
    return _request_file_bundle('bundle/{}'.format(bundle_id), 'PUT', file_hashes)


async def generate_bundle(file_hashes):
    """ Generate bundles via API. Incapsulates all logic of our bundle protocol. """

    async def _complete_bundle(bundle_task):
        bundle_id, missing_files = await bundle_task
        while(missing_files):
            await fulfill_bundle(bundle_id, missing_files) # Send all missing files
            missing_files = await check_bundle(bundle_id) # Check that all files are uploaded
        
        return bundle_id

    bundle_id = None
    
    with tqdm(total=len(file_hashes), desc='Generated bundles', unit='bundle', leave=False) as pbar:

        for chunked_files in chunks(int(MAX_BUCKET_SIZE // 200), file_hashes):
            
            if not bundle_id:
                bundle_id = await _complete_bundle( create_file_bundle(chunked_files) )
            else:
                bundle_id = await _complete_bundle( extend_file_bundle(bundle_id, chunked_files) )

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


async def check_bundle(bundle_id):
    """ Check missing files in bundle via API """
    data = await api_call('bundle/{}'.format(bundle_id), method='GET')
    return data['missingFiles']


async def upload_bundle_files(bundle_id, entries):
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
        callback=lambda resp: resp.text()
        )


async def fulfill_bundle(bundle_id, missing_files):
    """ Upload missing files to bundle via API """
    if not missing_files:
        return
    logger.debug('Uploading {} missing files'.format(len(missing_files)))
    with tqdm(total=len(missing_files), desc='Uploading missing files', unit='files', leave=False) as pbar:

        async def _wrap(chunk):
            await upload_bundle_files(bundle_id, chunk)
            pbar.update(len(chunk))

        tasks = [
            _wrap(chunk)
            for chunk in compose_file_buckets(missing_files)
        ]
        if tasks:
            await asyncio.wait(tasks)
        else:
            logger.debug('No new files sent, as all files have been uploaded earlier')
