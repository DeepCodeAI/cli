"""
A module dedicated to working with local folders/files.
"""
import os
import fnmatch
from itertools import chain
import hashlib

from .utils import logger

from .constants import (IGNORES_DEFAULT, IGNORE_FILES_NAMES, MAX_BUCKET_SIZE)

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
    for path in paths:
        with os.scandir(path) as it:
            local_files = []
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
                    
                    local_files.append(entry.path)
            
            if local_ignore_file:
                local_files = [p for p in local_files if not is_ignored(p, file_ignores)]
            
            yield from local_files

            sub_dirs = [
                subdir for subdir in sub_dirs
                if not is_ignored(subdir, file_ignores)
                ]
            yield from collect_bundle_files(sub_dirs, file_filter, file_ignores)


def get_file_meta(file_path):
    content = get_file_content(file_path)
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))

    return (len(content), hasher.hexdigest())


def prepare_bundle_hashes(bundle_files, bucket_size=MAX_BUCKET_SIZE):
    items = []
    for file_path in bundle_files:
        file_size, file_hash = get_file_meta(file_path)
        if file_size < bucket_size:
            items.append((file_path, file_hash))
    
    return items


def compose_file_buckets(file_paths, bucket_size=MAX_BUCKET_SIZE):
    """
    Splits files into buckets with limiting max size
    Returns list of items: (path, hash)
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
            logger.debug('ecxluded big file --> {} ({} bytes)'.format(file_path, file_size))
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
