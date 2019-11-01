import importlib.util
import sys
import os
from deepcode.src.constants.config_constants import DEEPCODE_PACKAGE_NAME


def handle_backend_host_last_slash(backend_host):
    last_symbol_index = len(backend_host)-1
    return backend_host[:last_symbol_index] if backend_host[last_symbol_index] == '/' else backend_host


def is_package_in_dev_mode():
    def dist_is_editable(dist):
        """Is distribution an editable install(develop mode)?"""
        for path_item in sys.path:
            egg_link = os.path.join(path_item, dist.name + '.egg-link')
            if os.path.isfile(egg_link):
                return True
        return False
    package = importlib.util.find_spec(DEEPCODE_PACKAGE_NAME)
    return dist_is_editable(package)
