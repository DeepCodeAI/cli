import json
from operator import itemgetter

SEVERITIES = {
    1: {
        'title': 'Info',
        'color': 'blue',
    },
    2: {
        'title': 'Warning',
        'color': 'yellow',
    },
    3: {
        'title': 'Critical',
        'color': 'red',
    },
}

# colors text background like marker
text_with_color_marker = {
    'blue': lambda sev: "\x1b[5;30;44m{}\x1b[0m".format(sev),
    'yellow': lambda sev: "\x1b[5;30;43m{}\x1b[0m".format(sev),
    'red': lambda sev: "\x1b[5;30;41m{}\x1b[0m".format(sev),
}

# colors text font
text_with_colors = {
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

SINGLELINE_POSITIONS_TEMPLATE = '{}line {}, symbols from {} to {}'
MULTILINE_POSITIONS_TEMPLATE = '{}lines from {} to {}, symbols from {} to {}'

def construct_severity_sub_header(severity_idx):
    color = SEVERITIES[severity_idx]['color']
    return text_with_color_marker[color](
        '{} issues'.format( SEVERITIES[severity_idx]['title'] )
    )


def construct_issue_txt_view(file_path, positions_list, severity, message):
    color = SEVERITIES[severity]['color']
    
    return '{filepath} {issue_msg}\n Issue positions:\n{positions}'.format(
        filepath=text_decorations['bold'](file_path),
        issue_msg=text_with_colors[color](message),
        positions=construct_issue_positions_txt_view(positions_list)
    )


def construct_issue_positions_txt_view(issues_positions_list):
    positions = []
    EXTRA_SPACES_FOR_POSITION = ' '*5
    for position in issues_positions_list:
        rows = position['rows']
        cols = position['cols']
        start_row, end_row = rows

        if start_row == end_row:
            item = SINGLELINE_POSITIONS_TEMPLATE.format(
                EXTRA_SPACES_FOR_POSITION, start_row, *cols)
        else:
            item = MULTILINE_POSITIONS_TEMPLATE.format(
                EXTRA_SPACES_FOR_POSITION, start_row, end_row, *cols)
        
        positions.append(item.rstrip())

        if 'markers' in position:
            positions.append(
                create_issue_markers_positions(position['markers'])
            )
    
    return '\n'.join(positions)


def create_issue_markers_positions(markers):
    EXTRA_SPACES_FOR_MARKERS_POSITION = ' '*10
    
    markers_positions = []
    for marker in markers:
        for pos in marker['pos']:
            cols = pos['cols']
            start_row, end_row = pos['rows']
            if start_row == end_row:
                marker_position = SINGLELINE_POSITIONS_TEMPLATE.format(
                        EXTRA_SPACES_FOR_MARKERS_POSITION, 
                        start_row, *cols)
                
            else:
                marker_position = MULTILINE_POSITIONS_TEMPLATE.format(
                        EXTRA_SPACES_FOR_MARKERS_POSITION, 
                        start_row, end_row, *cols)
            
            markers_positions.append(marker_position)
    
    if not markers_positions:
        return ''
    
    return '\n{}{}:\n{}'.format(
        EXTRA_SPACES_FOR_MARKERS_POSITION, 
        text_decorations['underlined']('issue helpers'), 
        '\n'.join(markers_positions))


def format_txt(data):
    """
    Presentation level. Parse json results into textual form.
    """
    
    url, results = itemgetter('url', 'results')(data)
    files, suggestions = itemgetter('files', 'suggestions')(results)
    if not len(files) and not len(suggestions):
        return text_with_colors['green']('Everything is fine. No issues found.')

    paragraphs = []

    grouped_issues = dict(zip(SEVERITIES.keys(), ([], [], [])))

    for file_path in files:
        for suggestion in files[file_path]:
            severity = suggestions[suggestion]['severity']
            issue_txt_view = construct_issue_txt_view(
                file_path,
                files[file_path][suggestion],
                severity,
                suggestions[suggestion]['message']
            )
            grouped_issues[severity].append(issue_txt_view)

    for severity, issues in sorted(grouped_issues.items(), key=lambda i: -i[0]):
        if issues:
            paragraphs.append(
                '\n'.join([
                    construct_severity_sub_header(severity), 
                    '\n'.join(issues)
                ])
            )
    
    paragraphs.extend([
        text_with_colors['green']('\n[Online analysis results]: '),
        text_decorations['underlined'](url),
    ])

    return '\n'.join(paragraphs)
