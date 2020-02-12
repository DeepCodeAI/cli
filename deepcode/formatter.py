import hashlib
import os
import io
import re
import json
from operator import itemgetter
from deepcode.src.constants.config_constants import MAX_REQUEST_BODY_SIZE, GIT_FOLDERNAME, GITIGNORE_FILENAME, SEVERITIES
from deepcode.src.helpers.terminal_view_decorations import text__with_colors, text_with__color_marker, text_decorations
from deepcode.src.helpers.cli_helpers import ANALYSIS_HELPERS

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
