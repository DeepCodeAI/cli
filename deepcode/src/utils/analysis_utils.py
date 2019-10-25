import hashlib
import os
import io
import multiprocessing
import fnmatch
import re
from concurrent.futures import ThreadPoolExecutor
from deepcode.src.constants.config_constants import MAX_FILE_SIZE, GIT_FOLDERNAME, GITIGNORE_FILENAME, SEVERITIES
from deepcode.src.constants.common_ignore_dirs import COMMON_IGNORE_DIRS
from deepcode.src.helpers.terminal_view_decorations import text__with_colors, text_with__color_marker, text_decorations


def hash_file_content(content):
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()


def hash_files(path, max_file_size, filters_dict, progress_iterator=lambda iterator, max_value: iterator):
    """
    Hash all files in a given folder
    :param max_file_size: files larger than this are not considered
    :param path: path to the folder
    :param filtering: only file paths for which this function returns true will be considered
    :param progress_iterator: function returning an iterator that can be used to inject progressbar outputs
    :return: dict of files pathes as keys and files hashes as values, e.g { [filepath]: filehash, ... }
    """
    paths = []
    gitignores = COMMON_IGNORE_DIRS
    progress_iterator_max_value = len(list(os.walk(path)))
    for root, dirs, files in progress_iterator(os.walk(path), max_value=progress_iterator_max_value):
        # parsing gitignore if it exists
        if GITIGNORE_FILENAME in files:
            gitignores.extend(parse_gitignore_file(root))

        # ignoring all git folders
        if GIT_FOLDERNAME in root:
            continue

        # threading checking folders in ignore folders
        is_root_in_ignore = False

        def thread_dir_result_cb(_):
            nonlocal is_root_in_ignore
            is_root_in_ignore = True
            return False
        if len(gitignores):
            execute_tasks_threads(
                threads_cb=lambda *p: regex_patterns_finder(root, ''.join(p)),
                thread_result_cb=thread_dir_result_cb,
                target=gitignores,
                kill_threads_on_success=True
            )

        if is_root_in_ignore:
            # os.walk will skip all inner dirs of ignored dir
            dirs[:] = []
            continue
        # filtering files
        for f in files:
            file_path = os.path.join(root, f)
            rel_path = os.path.relpath(file_path, path)
            if pass_filter(rel_path, filters_dict):
                paths.append((file_path, rel_path))

    result = {}
    # threading creations of hashes

    def thread_file_result_cb(path_hash_tuple):
        file_path, file_hash = path_hash_tuple
        result[file_path] = file_hash
    execute_tasks_threads(
        threads_cb=lambda *p: create_file_hash_with_path(max_file_size, p),
        thread_result_cb=thread_file_result_cb,
        target=paths
    )
    return result


def execute_tasks_threads(
    threads_cb,
    thread_result_cb,
    target,
    kill_threads_on_success=False
):
    with ThreadPoolExecutor(max_workers=multiprocessing.cpu_count()) as threads_executor:
        def thread_function(p):
            return threads_executor.submit(threads_cb, *p)
        futures = list(map(thread_function, target))
        for f in futures:
            res = f.result()
            if res:
                thread_result_cb(res)
                if kill_threads_on_success:
                    threads_executor.shutdown(wait=False)
                    break


def create_file_hash_with_path(max_file_size, path_list):
    abs_path_, rel_path_ = path_list
    file_content = file_contents_as_string(abs_path_, max_file_size)
    if not file_content:
        return None
    file_hash = hash_file_content(file_content)

    return rel_path_, file_hash


def file_contents_as_string(path, max_file_size=MAX_FILE_SIZE):
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


def parse_gitignore_file(root):
    with open(os.path.join(root, GITIGNORE_FILENAME)) as gitignore_file:
        return gitignore_file.read().splitlines()


def extract_data_from_remote_bundle_path(bundle_path):
    result = {
        'owner': None,
        'repo': None,
        'oid': None
    }
    no_data_count, part_data_count, all_data_count = (1, 2, 3)
    splitted = bundle_path.split('/')
    if len(splitted) is no_data_count:
        return result
    if len(splitted) >= part_data_count:
        [owner, repo, *_] = splitted
        result['owner'] = owner
        result['repo'] = repo
    if len(splitted) is all_data_count:
        [*_, commit] = splitted
        result['oid'] = commit
    return result


def validate_data_for_remote(remote_data):
    return not all(remote_data[key] is None for key in remote_data)


def pass_filter(file, filters_dict):
    if file in filters_dict['configFiles']:
        return True
    if '.{}'.format(file.split('.')[-1]) in filters_dict['extensions']:
        return True
    return False


def regex_patterns_finder(path, pattern):
    try:
        return bool(re.search(pattern, path))
    except:
        return False


def construct_issue_txt_view(
    issue_file_path,
    issues_positions_list,
    issue_severity_number,
    issue_message
):
    severities_colors = {
        1: 'blue',
        2: 'yellow',
        3: 'red',
    }
    severity_color = severities_colors[issue_severity_number]
    with_severity_color = text__with_colors[severity_color]
    with_severity_marker = text_with__color_marker[severity_color]
    positions_of_issue_str = construct_issue_positions_txt_view(
        issues_positions_list)

    template_str = '{filepath}   {severity} {issue_msg}\n Issue positions:\n{positions}'
    return template_str.format(
        filepath=text_decorations['bold'](issue_file_path),
        severity=with_severity_marker(SEVERITIES[issue_severity_number]),
        issue_msg=with_severity_color(issue_message),
        positions=positions_of_issue_str
    )


def construct_issue_positions_txt_view(issues_positions_list):
    positions_of_issue_str = ''
    EXTRA_SPACES_FOR_POSITION = ' '*5
    singleline_issue_template_str = '{}line {}, symbols from {} to {}'
    multiline_issue_template_str = '{}lines from {} to {}, symbols from {} to {}'
    for idx, position in enumerate(issues_positions_list):
        rows, cols = position.values()
        start_row, end_row = rows
        if start_row == end_row:
            positions_of_issue_str += singleline_issue_template_str.format(
                EXTRA_SPACES_FOR_POSITION, start_row, *cols)
        else:
            positions_of_issue_str += multiline_issue_template_str.format(
                EXTRA_SPACES_FOR_POSITION, start_row, end_row, *cols)
        if idx is not len(issues_positions_list)-1:
            positions_of_issue_str += '\n'
    return positions_of_issue_str
