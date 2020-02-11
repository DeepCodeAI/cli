import asyncio
import os

from .files import prepare_bundle_files
from .bundle import get_filters, generate_bundles, create_git_bundle, fulfill_bundle, check_bundle
from .analysis import get_analysis
from .utils import logger, profile_speed


@profile_speed
async def analize_folders(paths, linters_enabled=False):
    """ Entire flow of analyzing local folders. """
    file_filter = await get_filters()

    file_hashes = prepare_bundle_files(paths, file_filter)
    logger.info('Files to be analyzed --> {}'.format( len(file_hashes) ))

    async for bundle_id, missing_files in generate_bundles(file_hashes):
        
        while(missing_files):
            await fulfill_bundle(bundle_id, missing_files)
            
            missing_files = await check_bundle(bundle_id)
    
    return await get_analysis(bundle_id, linters_enabled=linters_enabled)


@profile_speed
async def analize_git(platform, owner, repo, oid=None, linters_enabled=False):
    """ Entire flow of analyzing remote git repositories. """
    bundle_id = await create_git_bundle(platform, owner, repo, oid)
    
    return await get_analysis(bundle_id, linters_enabled=linters_enabled)

