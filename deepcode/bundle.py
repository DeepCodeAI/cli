import os
import json
import asyncio
import time
from funcy import chunks

from .connection import api_call
from .files import get_file_content, compose_file_buckets, MAX_BUCKET_SIZE
from .utils import profile_speed, logger

@profile_speed
async def get_filters():
    """ Fetch supported file extensions """
    filters = await api_call('filters')
    logger.debug('filters --> {}'.format(filters))
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

@profile_speed
async def create_file_bundle(file_hashes):
    """ Create a new bundle via API  """
    return await _request_file_bundle('bundle', 'POST', file_hashes)

@profile_speed
async def extend_file_bundle(bundle_id, file_hashes):
    """ Extend bundle via API  """
    return await _request_file_bundle('bundle/{}'.format(bundle_id), 'PUT', file_hashes)


async def generate_bundles(file_hashes):
    """ Generate bundles via API. Split files into chunks. """

    bundle_id, missing_files = None, []
    
    for index, chunked_files in enumerate(chunks(int(MAX_BUCKET_SIZE // 200), file_hashes)):
        logger.debug('#{} chunk with {} files'.format(index, len(chunked_files)))
        if not bundle_id:
            bundle_id, missing_files = await create_file_bundle(chunked_files)
        else:
            bundle_id, missing_files = await extend_file_bundle(bundle_id, chunked_files)

        yield bundle_id, missing_files
    

@profile_speed
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

@profile_speed
async def check_bundle(bundle_id):
    """ Check missing files in bundle via API """
    data = await api_call('bundle/{}'.format(bundle_id), method='GET')
    return data['missingFiles']


async def upload_bundle_files(bundle_id, entries):
    """
    Each entry should contain of: (path, hash)
    """
    start_time = time.time()
    
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

    logger.debug('{:10.2f} sec | sent {} files'.format(
        time.time() - start_time, 
        len(entries)
        ))


@profile_speed
async def fulfill_bundle(bundle_id, missing_files):
    """ Upload missing files to bundle via API """
    if not missing_files:
        return
    
    tasks = [
        upload_bundle_files(bundle_id, chunk)
        for chunk in compose_file_buckets(missing_files)
    ]
    if tasks:
        await asyncio.gather(*tasks)
    else:
        logger.info('No new files sent, as all files have been uploaded earlier')
