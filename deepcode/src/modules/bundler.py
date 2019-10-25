import progressbar
from deepcode.src.constants.config_constants import MAX_FILE_SIZE
from deepcode.src.constants.cli_constants import MAX_PROGRESS_VALUE
from deepcode.src.utils.analysis_utils\
    import hash_files, file_contents_as_string


class DeepCodeBundler:
    def __init__(self):
        pass

    def create_hashes_bundle(self, bundle_path, filters_dict):
        return hash_files(
            bundle_path,
            MAX_FILE_SIZE,
            filters_dict,
            progress_iterator=lambda iterator, max_value: progressbar.progressbar(
                iterator, max_value=max_value, prefix="DeepCode creating bundle progress: ")
        )

    def create_missing_files_batch(self, missing_files, hashes_bundle):
        missing_files_batch = []
        for file_path in missing_files:
            path = file_path[1:] if file_path[0] == '/' else file_path
            file_hash = hashes_bundle[path]
            file_content = file_contents_as_string(path)
            if file_content is not None:
                missing_files_batch.append(
                    {'fileHash': file_hash, 'fileContent': file_content})
        return missing_files_batch
