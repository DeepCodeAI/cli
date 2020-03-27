def filter_severity(analysis_results, severity):
    """
    Exclude all suggestions with severity lower, then specified.
    Makes this exclusion in-place, no value returned or copied.
    This is done in purpose, as we plan to implement this logic inside Bundle server later; and then remove this function.
    """

    if severity == 1:
        return analysis_results

    suggestions = {
        k:v
        for k, v in analysis_results['suggestions'].items()
        if v['severity'] >= severity
    }

    files = {}
    for f_path, f_suggestions in analysis_results['files'].items():
        filtered_suggestions = {
            f_id: f_data
            for f_id, f_data in f_suggestions.items()
            if f_id in suggestions.keys()
        }
        if filtered_suggestions:
            files[f_path] = filtered_suggestions


    return {
        'suggestions': suggestions,
        'files': files
    }
