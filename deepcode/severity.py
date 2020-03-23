def filter_severity(analysis_data, severity):
    """
    Exclude all suggestions with severity lower, then specified.
    Makes this exclusion in-place, no value returned or copied.
    This is done in purpose, as we plan to implement this logic inside Bundle server later; and then remove this function.
    """

    severity = {
        'info': 1,
        'warning': 2,
        'critical': 3
        }.get(severity) or 1

    if severity == 1:
        return

    suggestions = {
        k:v
        for k, v in analysis_data['results']['suggestions'].items()
        if v['severity'] >= severity
    }

    files = {}
    for f_path, f_suggestions in analysis_data['results']['files'].items():
        filtered_suggestions = {
            f_id: f_data
            for f_id, f_data in f_suggestions.items()
            if f_id in suggestions.keys()
        }
        if filtered_suggestions:
            files[f_path] = filtered_suggestions


    analysis_data['results'].update({
        'suggestions': suggestions,
        'files': files
    })
