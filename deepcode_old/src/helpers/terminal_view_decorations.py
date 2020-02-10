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
