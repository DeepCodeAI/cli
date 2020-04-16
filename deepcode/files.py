"""
A module dedicated to working with local folders/files.
"""
import os
from copy import copy
import fnmatch
from itertools import chain
import hashlib

from .utils import logger

from .constants import (IGNORES_DEFAULT, IGNORE_FILES_NAMES, MAX_BUCKET_SIZE)

def prepare_file_path(filepath):
    """
    1. Get relative path
    2. Modify Windows path
    3. Prefix with /
    """
    relpath = os.path.relpath(filepath).replace('\\', '/')
    return '/{}'.format(relpath)

def resolve_file_path(bundle_filepath):
    """ Reversive function to prepare_file_path """
    path = bundle_filepath[1:]

    if os.name != 'posix':
        path = path.replace('/', '\\')

    return os.path.abspath(path)

def get_file_content(file_path):
    with open(file_path, encoding='utf-8', mode='r') as f:
        return f.read()

def parse_file_ignores(file_path):
    dirname = os.path.dirname(file_path)
    with open(file_path, encoding='utf-8', mode='r') as f:
        for l in f.readlines():
            rule = l.strip().rstrip('/') # Trim whitespaces and ending slash
            if rule and not rule.startswith('#'):
                yield os.path.join(dirname, rule)
                if not rule.startswith('/'):
                    yield os.path.join(dirname, '**', rule)


def is_ignored(path, file_ignores):
    for i in file_ignores:
        if fnmatch.fnmatch(path, i):
            logger.debug('pattern: {} | ignored: {}'.format(i, path))
            return True

    return False


def collect_bundle_files(paths, file_filter, symlinks_enabled=False, file_ignores=IGNORES_DEFAULT):
    local_file_ignores = copy(file_ignores)
    for path in paths:
        # Check if symlink and exclude if requested
        if os.path.islink(path) and not symlinks_enabled:
            continue

        if os.path.isfile(path):
            if file_filter(path) and not is_ignored(path, file_ignores):
                yield path
        elif os.path.isdir(path):
            with os.scandir(path) as it:
                local_files = []
                sub_dirs = []
                local_ignore_file = False
                for entry in it:

                    if entry.is_symlink() and not symlinks_enabled:
                        continue

                    if entry.is_dir(follow_symlinks=symlinks_enabled):
                        sub_dirs.append(entry.path)
                        continue

                    if entry.name in IGNORE_FILES_NAMES:
                        for ignore_rule in parse_file_ignores(entry.path):
                            local_file_ignores.add(ignore_rule)
                        local_ignore_file = True
                        logger.debug('recognized ignore rules in file --> {}'.format(entry.path))
                        continue

                    if entry.is_file(follow_symlinks=symlinks_enabled) \
                    and file_filter(entry.name) \
                    and not is_ignored(entry.path, local_file_ignores):
                        local_files.append(entry.path)

                if local_ignore_file:
                    local_files = [p for p in local_files if not is_ignored(p, local_file_ignores)]

                yield from local_files

                sub_dirs = [
                    subdir for subdir in sub_dirs
                    if not is_ignored(subdir, local_file_ignores)
                    ]
                yield from collect_bundle_files(sub_dirs, file_filter, symlinks_enabled, local_file_ignores)


def get_file_meta(file_path):
    content = get_file_content(file_path)
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))

    return (len(content), hasher.hexdigest())


def prepare_bundle_hashes(bundle_files, bucket_size=MAX_BUCKET_SIZE):
    items = []
    for file_path in bundle_files:
        try:
            file_size, file_hash = get_file_meta(file_path)
        except UnicodeDecodeError:
            logger.debug('ecxluded a file --> {} (Unicode Decode Error)'.format(file_path))
        else:
            if file_size < bucket_size:
                items.append((file_path, file_hash))

    return items


def compose_file_buckets(missing_files, bucket_size=MAX_BUCKET_SIZE):
    """
    Splits files into buckets with limiting max size
    Returns list of items: (path, hash)
    """
    buckets = [{
        'size': bucket_size,
        'files': []
    }]

    def route_file_to_bucket(raw_file_path):

        file_path = resolve_file_path(raw_file_path)

        # Get file details
        file_size, file_hash = get_file_meta(file_path)

        # Check that file does not exceed max bucket size
        if file_size > bucket_size:
            logger.debug('excluded big file --> {} ({} bytes)'.format(file_path, file_size))
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

    for raw_file_path in missing_files:
        bucket = route_file_to_bucket(raw_file_path)
        if not bucket:
            continue

        if bucket['size'] < bucket_size * 0.01:
            yield bucket['files'] # Give bucket to requester
            buckets.remove(bucket) # Remove it as fullfilled

    # Send all left-over buckets
    for bucket in buckets:
        if bucket['files']:
            yield bucket['files']
