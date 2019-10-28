"""
    DeepCode module for analyzing code.\n
    Avaliable methods:\n
        analyze([path: string(optional)], [repo: boolean](optional)):
            
            :return - json with results or json with 'error' e.g. {"error": "[text of error]"}. 
            Will perform code analysis for specified path.
            Can accept absolute path or path to git bundle in format [user_name]/[repo_name]/[commit(optional)]
            
"""
from deepcode.src.module import deepcode_module

name = "deepcode"
description = "This package is avaliable as imported module and as cli tool. To use it as imported module, please import it and call start() method with args. To use it in terminal, just call deepcode in terminal and pass args"

# avaliable methods for module
def analyze(path=None, is_repo=False): return deepcode_module.analyze(
    path, is_repo)
