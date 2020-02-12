import asyncio
import os
from tqdm import tqdm

from .files import collect_bundle_files, prepare_bundle_hashes
from .bundle import get_filters, generate_bundle, create_git_bundle
from .analysis import get_analysis
from .utils import logger, profile_speed


@profile_speed
async def analize_folders(paths, linters_enabled=False):
    """ Entire flow of analyzing local folders. """
    
    with tqdm(total=5, desc='Analizing folders', unit='step', leave=False) as pbar:

        pbar.set_description('Fetching supported extensions')
        file_filter = await get_filters()
        pbar.update(1)

        pbar.set_description('Scanning for files')
        bundle_files = collect_bundle_files(paths, file_filter)
        bundle_files = tuple(
            tqdm(bundle_files, desc='Found files', unit='f', leave=False) # progress bar
        )
        pbar.update(1)

        pbar.set_description('Computing file hashes')
        file_hashes = prepare_bundle_hashes(
            tqdm(bundle_files, desc='Calculated hashes', unit='files', leave=False) # progress bar
            )
        pbar.update(1)

        pbar.set_description('Sending data')
        
        bundle_id  = await generate_bundle(file_hashes)
        pbar.update(1)

        pbar.set_description('Requesting audit results')
        res = await get_analysis(bundle_id, linters_enabled=linters_enabled)
        pbar.update(1)
        pbar.set_description('Finished analysis')

        return res


async def analize_git(platform, owner, repo, oid=None, linters_enabled=False):
    """ Entire flow of analyzing remote git repositories. """
    bundle_id = await create_git_bundle(platform, owner, repo, oid)
    
    return await get_analysis(bundle_id, linters_enabled=linters_enabled)

