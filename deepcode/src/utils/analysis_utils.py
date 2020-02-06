import hashlib
import os
import io
import re
import json
from operator import itemgetter
from deepcode.src.constants.config_constants import MAX_REQUEST_BODY_SIZE, GIT_FOLDERNAME, GITIGNORE_FILENAME, SEVERITIES
from deepcode.src.helpers.terminal_view_decorations import text__with_colors, text_with__color_marker, text_decorations
from deepcode.src.helpers.cli_helpers import ANALYSIS_HELPERS


def hash_file_content(content):
    hasher = hashlib.sha256()
    hasher.update(content.encode('utf-8'))
    return hasher.hexdigest()


def hash_files(path, max_file_size, filters_dict, show_progressbar=True, progress_iterator=lambda iterator, max_value: iterator):
    """
    Hash all files in a given folder
    :param max_file_size: files larger than this are not considered
    :param path: path to the folder
    :param filtering: only file paths for which this function returns true will be considered
    :param progress_iterator: function returning an iterator that can be used to inject progressbar outputs
    :return: dict of files pathes as keys and files hashes as values, e.g { [filepath]: filehash, ... }
    """
    paths = []

    ignores = []
    progress_iterator_max_value = len(list(os.walk(path)))
    iteratable_range = progress_iterator(os.walk(
        path), max_value=progress_iterator_max_value) if show_progressbar else os.walk(path)
    for root, dirs, files in iteratable_range:
        # parsing gitignore if it exists
        if GITIGNORE_FILENAME in files:
            ignores.extend(parse_gitignore_file(root))

        # ignoring all git folders
        if GIT_FOLDERNAME in root:
            continue
        if len(ignores):
            ignore = next(
                (ignore for ignore in ignores if regex_patterns_finder(root, ignore)), None)
            if ignore:
                # os.walk will skip all inner dirs of ignored dir
                dirs[:] = []
                continue
        # filtering files
        for f in files:
            file_path = os.path.join(root, f)
            if pass_filter(file_path, filters_dict):
                paths.append(file_path)
    result = {}
    # creations of hashes
    for path in paths:
        path_hash_tuple = create_file_hash_with_path(max_file_size, path)
        if path_hash_tuple:
            file_path, file_hash = path_hash_tuple
            result[file_path] = file_hash
    return result


def create_file_hash_with_path(max_file_size, file_path):
    file_content = file_contents_as_string(file_path, max_file_size)
    if not file_content:
        return None
    
    return file_path, hash_file_content(file_content)


def file_contents_as_string(path, max_file_size=MAX_REQUEST_BODY_SIZE):
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
        return [line for line in gitignore_file.read().splitlines() if line and line[0] is not '#']


def extract_data_from_remote_bundle_path(bundle_path):
    result = {
        'owner': None,
        'repo': None,
        'oid': None
    }
    no_data_count, part_data_count, all_data_count = (1, 2, 3)
    splitted = bundle_path.split('/')
    if len(splitted) and not splitted[0]:
        splitted = splitted[1:]
    if len(splitted) > all_data_count:
        return result
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


def get_severities_colors():
    return {
        1: 'blue',
        2: 'yellow',
        3: 'red',
    }


def construct_severity_sub_header(severity_idx):
    severity_color = get_severities_colors()[severity_idx]
    sub_header_text = '{} issues'.format(SEVERITIES[severity_idx])
    return text_with__color_marker[severity_color](sub_header_text)


def construct_issue_txt_view(
    issue_file_path,
    issues_positions_list,
    issue_severity_number,
    issue_message
):
    severities_colors = get_severities_colors()

    severity_color = severities_colors[issue_severity_number]
    with_severity_color = text__with_colors[severity_color]
    positions_of_issue_str = construct_issue_positions_txt_view(
        issues_positions_list)

    template_str = '{filepath} {issue_msg}\n Issue positions:\n{positions}'
    return template_str.format(
        filepath=text_decorations['bold'](issue_file_path),
        issue_msg=with_severity_color(issue_message),
        positions=positions_of_issue_str
    )


def create_singleline_positions_template_str():
    return '{}line {}, symbols from {} to {}'


def create_multiline_poitions_template_str():
    return '{}lines from {} to {}, symbols from {} to {}'


def construct_issue_positions_txt_view(issues_positions_list):
    positions_of_issue_str = ''
    EXTRA_SPACES_FOR_POSITION = ' '*5
    singleline_issue_template_str = create_singleline_positions_template_str()
    multiline_issue_template_str = create_multiline_poitions_template_str()
    for idx, position in enumerate(issues_positions_list):
        rows = position['rows']
        cols = position['cols']
        start_row, end_row = rows
        if start_row == end_row:
            positions_of_issue_str += singleline_issue_template_str.format(
                EXTRA_SPACES_FOR_POSITION, start_row, *cols)
        else:
            positions_of_issue_str += multiline_issue_template_str.format(
                EXTRA_SPACES_FOR_POSITION, start_row, end_row, *cols)
        if 'markers' in position:
            positions_of_issue_str += create_issue_markers_positions(
                position['markers'])
        if idx is not len(issues_positions_list)-1:
            positions_of_issue_str += '\n'
    return positions_of_issue_str


def create_issue_markers_positions(markers):
    EXTRA_SPACES_FOR_MARKERS_POSITION = ' '*10
    singleline_issue_template_str = create_singleline_positions_template_str()
    multiline_issue_template_str = create_multiline_poitions_template_str()
    markers_subheader_str = '\n{}{}:\n'.format(
        EXTRA_SPACES_FOR_MARKERS_POSITION, text_decorations['underlined']('issue helpers'))
    markers_positions_str = ''
    for marker in markers:
        for pos in marker['pos']:
            cols = pos['cols']
            start_row, end_row = pos['rows']
            if start_row == end_row:
                markers_positions_str += singleline_issue_template_str.format(
                    EXTRA_SPACES_FOR_MARKERS_POSITION, start_row, *cols)+'\n'
            else:
                markers_positions_str += multiline_issue_template_str.format(
                    EXTRA_SPACES_FOR_MARKERS_POSITION, start_row, end_row, *cols)+'\n'
    return '{}{}'.format(markers_subheader_str, markers_positions_str.rstrip())


def construct_issues_complex_txt_view(analysis_results, is_silent=False):
    result_txt = '' if is_silent else '{}\n'.format(
        ANALYSIS_HELPERS['txt_view_results'])
    files, suggestions = itemgetter(
        'files', 'suggestions')(analysis_results)
    if not len(files) and not len(suggestions):
        return ANALYSIS_HELPERS['empty_results']

    info, warning, critical = SEVERITIES.keys()
    grouped_issues = {
        critical: '',
        warning: '',
        info: ''
    }

    for file_index, file_path in enumerate(files):
        issue_file_path = file_path
        for suggestion in files[file_path]:
            issues_positions_list = files[file_path][suggestion]
            issue_severity_number = suggestions[suggestion]['severity']
            issue_message = suggestions[suggestion]['message']
            issue_txt_view = construct_issue_txt_view(
                issue_file_path,
                issues_positions_list,
                issue_severity_number,
                issue_message
            )
            grouped_issues[issue_severity_number] += '{}\n'.format(
                issue_txt_view)

    for idx, severity in enumerate(grouped_issues):
        if grouped_issues[severity]:
            result_txt += '{}\n{}'.format(
                construct_severity_sub_header(severity), grouped_issues[severity].rstrip())
            if idx < len(grouped_issues)-1:
                result_txt += '\n'
    return result_txt


def construct_issues_json_view(analysis_results, is_silent=False):
    if is_silent:
        return '{}'.format(json.dumps(analysis_results))
    return '{}\n{}'.format(ANALYSIS_HELPERS['json_view_results'], json.dumps(analysis_results))
