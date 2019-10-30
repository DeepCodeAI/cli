import progressbar
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE


def construct_progress(prefix, min_value=0, max_value=MAX_PROGRESS_VALUE):
    return \
        progressbar.ProgressBar(
            max_value=max_value, min_value=min_value, prefix=prefix)


def progress_iterator(prefix):
    return lambda iterator, max_value: progressbar.progressbar(
        iterator, max_value=max_value, prefix=prefix)
