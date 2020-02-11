import os
import fnmatch
import aiofiles
import asyncio
from funcy import lcat, project
from itertools import chain
import hashlib

from .utils import profile_speed, logger

IGNORES_DEFAULT = {
    '**/.git',
}

IGNORE_FILES_NAMES = {
    '.gitignore',
    '.dcignore'
}

MAX_BUCKET_SIZE = 1024 * 1024 * 4

def get_file_content(file_path):
    with open(file_path, mode='r') as f:
        return f.read()

def parse_file_ignores(file_path):
    dirname = os.path.dirname(file_path)
    with open(file_path, mode='r') as f:
        for l in f.readlines():
            rule = l.strip()
            if not rule.startswith('#'):
                yield os.path.join(dirname, rule)

def is_ignored(path, file_ignores):
    return any(i for i in file_ignores if fnmatch.fnmatch(path, i))
    

def collect_bundle_files(paths, file_filter, file_ignores=IGNORES_DEFAULT):
    local_files = []
    
    for path in paths:
        with os.scandir(path) as it:
            sub_dirs = []
            local_ignore_file = False
            for entry in it:

                if entry.is_symlink():
                    # To prevent possible infinite loops, we ignore symlinks for now
                    continue
                
                if entry.is_dir():
                    sub_dirs.append(entry.path)
                    continue

                if entry.name in IGNORE_FILES_NAMES:
                    for ignore_rule in parse_file_ignores(entry.path):
                        file_ignores.add(ignore_rule)
                    local_ignore_file = True
                    logger.debug('recognized ignore rules in file --> {}'.format(entry.path))
                    continue 
                
                if entry.is_file() \
                and not is_ignored(entry.path, file_ignores) \
                and file_filter(entry.name):
                    
                    local_files.append(entry)
            
            if local_ignore_file:
                local_files = [f for f in local_files if not is_ignored(f.path, file_ignores)]
            
            sub_dirs = [
                subdir for subdir in sub_dirs
                if not is_ignored(subdir, file_ignores)
                ]
            results = collect_bundle_files(sub_dirs, file_filter, file_ignores) 
            local_files.extend(results)
    
    return local_files


def get_file_meta(file_path):
    
    # stat = os.stat(file_path)
    # sg = lambda f: getattr(stat, f, '')
    # hasher.update('{}{}{}{}'.format(
    #     stat.st_size, sg('st_rsize'), # file sizes
    #     sg('st_mtime'), # modified
    #     sg('st_type') # file type
    #     ).encode('utf-8') )
    
    content = get_file_content(file_path)
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))

    return (len(content), hasher.hexdigest())


def prepare_bundle_hashes(bundle_files, bucket_size=MAX_BUCKET_SIZE):
    items = []
    for entry in bundle_files:
        file_size, file_hash = get_file_meta(entry.path)
        if file_size < bucket_size:
            items.append((entry.path, file_hash))
    
    return items


@profile_speed
def prepare_bundle_files(paths, file_filter):
    """ Prepare files for bundle. """
    bundle_files = collect_bundle_files(paths, file_filter)
    return prepare_bundle_hashes(bundle_files)


def compose_file_buckets(file_paths, bucket_size=MAX_BUCKET_SIZE):
    """
    Split files into buckets with limiting max size
    Return list of items: (path, hash, size)
    """
    buckets = [{
        'size': bucket_size,
        'files': []
    }]

    def route_file_to_bucket(file_path):
        # Get file details
        file_size, file_hash = get_file_meta(file_path)

        # Check that file does not exceed max bucket size
        if file_size > bucket_size:
            return

        # Try to find existing bucket
        for bucket in buckets:
            if bucket['size'] >= file_size:
                bucket['files'].append( (file_path, file_hash) )
                bucket['size'] -= file_size
                return bucket
        
        bucket = {
            'size': bucket_size - file_size,
            'files': [ (file_path, file_hash) ]
        }
        buckets.append(bucket)
        return bucket
    
    for file_path in file_paths:
        bucket = route_file_to_bucket(file_path)
        if not bucket:
            continue

        if bucket['size'] < bucket_size * 0.01:
            yield bucket['files'] # Give bucket to requester
            buckets.remove(bucket) # Remove it as fullfilled
    
    # Send all left-over buckets
    for bucket in buckets:
        if bucket['files']:
            yield bucket['files']
