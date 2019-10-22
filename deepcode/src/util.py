"""
Copyright 2019 DeepCode AG

Author: Jan Eberhardt
"""

import hashlib
import os
import io
import multiprocessing
from concurrent.futures import ThreadPoolExecutor


def hash_file_content(content):
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()


def hash_files(path, max_file_size, filtering=lambda path: True, progress_iterator=lambda iterator: iterator):
    """
    Hash all files in a given folder
    :param max_file_size: files larger than this are not considered
    :param path: path to the folder
    :param filtering: only file paths for which this function returns true will be considered
    :param progress_iterator: function returning an iterator that can be used to inject progressbar outputs
    :return: list uf tuples of file hashes and relative paths
    """
    # prepare paths, list of tuples of absolute path and relative path
    paths = []
    for root, dirs, files in os.walk(path):
        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, path)
            if filtering(rel_path):
                paths.append((file_path, rel_path))

    def handle_path(abs_path_, rel_path_):
        file_content = file_contents_as_string(abs_path_, max_file_size)
        if not file_content:
            return None
        file_hash = hash_file_content(file_content)
        return file_hash, rel_path_

    result = []

    # deepcode ignore add~shutdown~concurrent.futures.ThreadPoolExecutor: <please specify a reason of ignoring this>
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
        # submit futures
        futures = list(map(lambda p: executor.submit(handle_path, *p), paths))
        # wait for future completion, show progress
        for f in progress_iterator(futures):
            res = f.result()
            if res:
                result.append(res)
    return result


def file_contents_as_string(path, max_file_size):
    """
    Read contents of file as utf-8 string
    :param path: absolute path to the file
    :param max_file_size: if the file is larger than this, None is returned
    :return: file content as utf-8 string or None if file is too large
    """
    if os.path.getsize(path) >= max_file_size:
        return None
    with io.open(path, mode='r', encoding='utf-8', errors='ignore') as f:
        return f.read()


def utf8len(utf8_str):
    return len(utf8_str.encode('utf-8'))
