import asyncio
import logging
import os
import time

from .files import collect_bundle_files, prepare_bundle_hashes
from .bundle import get_filters, create_bundle, fulfill_bundle, check_bundle
from .analysis import get_analysis

logging.basicConfig(level=logging.DEBUG)

PATH = '/Users/arvid/workspace/test/DefinitelyTyped'
#PATH = '/Users/arvid/workspace/dc/cli'

LINTERS_ENABLED = False

async def main(path):
    start_time = time.time()
    filters = await get_filters()
    print("--- {:10.2f} sec for getting filters ---".format(time.time() - start_time))
    
    supported_extensions = set(filters['extensions'])
    expected_config_files = set(filters['configFiles'])
    file_filter = lambda n: os.path.splitext(n)[-1] in supported_extensions or n in expected_config_files

    bundle_files = []
    
    start_time = time.time()
    bundle_files = await collect_bundle_files(path, file_filter)
    print('bundle_files --> ', len(bundle_files))
    print("--- {:10.2f} sec for collect_bundle_files ---".format(time.time() - start_time))

    start_time = time.time()
    file_hashes = prepare_bundle_hashes(bundle_files)
    print("--- {:10.2f} sec for prepare_bundle_hashes ---".format(time.time() - start_time))

    start_time = time.time()
    bundle_id, missing_files = await create_bundle(file_hashes)
    #print('bundle --> ', bundle)
    print("--- {:10.2f} sec for create_bundle ---".format(time.time() - start_time))

    while(missing_files):
        start_time = time.time()
        await fulfill_bundle(bundle_id, missing_files)
        print("--- {:10.2f} sec for fulfill_bundle ---".format(time.time() - start_time))

        start_time = time.time()
        missing_files = await check_bundle(bundle_id)
        print("--- {:10.2f} sec for check_bundle ---".format(time.time() - start_time))
        
    
    start_time = time.time()
    missing_files = await get_analysis(bundle_id, linters_enabled=LINTERS_ENABLED)
    print("--- {:10.2f} sec for get_analysis ---".format(time.time() - start_time))


def run_main_loop(path):
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(path))
    loop.run_until_complete(loop.shutdown_asyncgens())
    