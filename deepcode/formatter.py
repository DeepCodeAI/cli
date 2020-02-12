import json
from operator import itemgetter
#from deepcode.src.constants.config_constants import SEVERITIES

SEVERITIES_COLOR = {
    1: 'blue',
    2: 'yellow',
    3: 'red',
}

# colors text background like marker
text_with__color_marker = {
    'blue': lambda sev: "\x1b[5;30;44m{}\x1b[0m".format(sev),
    'yellow': lambda sev: "\x1b[5;30;43m{}\x1b[0m".format(sev),
    'red': lambda sev: "\x1b[5;30;41m{}\x1b[0m".format(sev),
}

# colors text font
text__with_colors = {
    # blue text for info
    'blue': lambda text: "\33[94m{}\33[0m".format(text),
    # yellow text for warnings
    'yellow': lambda text: "\33[93m{}\33[0m".format(text),
    # red text for critical or errors
    'red': lambda text: "\33[91m{}\33[0m".format(text),
    # green color for success
    'green': lambda text: "\33[92m{}\33[0m".format(text),
}

text_decorations = {
    'bold': lambda t: "\33[1m{}\33[0m".format(t),
    'underlined': lambda t: '\033[4m{}\033[0m'.format(t)
}

def construct_severity_sub_header(severity_idx):
    severity_color = SEVERITIES_COLOR[severity_idx]
    sub_header_text = '{} issues'.format(SEVERITIES[severity_idx])
    return text_with__color_marker[severity_color](sub_header_text)


def construct_issue_txt_view(
    issue_file_path,
    issues_positions_list,
    issue_severity_number,
    issue_message
):
    severity_color = SEVERITIES_COLOR[issue_severity_number]
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


def construct_issues_complex_txt_view(analysis_results):
    result_txt = '{}'.format(ANALYSIS_HELPERS['txt_view_results'])
    files, suggestions = itemgetter('files', 'suggestions')(analysis_results)
    if not len(files) and not len(suggestions):
        return ANALYSIS_HELPERS['empty_results']

    info, warning, critical = SEVERITIES.keys()
    grouped_issues = {
        critical: [],
        warning: [],
        info: []
    }

    for file_path in files:
        for suggestion in files[file_path]:
            issue_severity = suggestions[suggestion]['severity']
            issue_txt_view = construct_issue_txt_view(
                file_path,
                files[file_path][suggestion],
                issue_severity,
                suggestions[suggestion]['message']
            )
            grouped_issues[issue_severity].append(issue_txt_view)

    for idx, severity in enumerate(grouped_issues):
        if grouped_issues[severity]:
            result_txt += '{}\n{}'.format(
                construct_severity_sub_header(severity), 
                grouped_issues[severity].rstrip())
            if idx < len(grouped_issues)-1:
                result_txt += '\n'
    return result_txt


ANALYSIS_HELPERS = {
    'txt_view_results': text__with_colors['green']('DeepCode Analysis Results in text format:'),
    'empty_results': text__with_colors['green']('Everything is fine. No issues found.')
}
