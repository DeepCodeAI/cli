"""
    DeepCode module for analyzing code.\n
    Avaliable methods:\n
        analyze([path], [is_repo: boolean]): -> return json object
            :param [path] - absolute path to bundle dir or path to remote repo of current registered user e.g.[user_name]/[repo_name]/[commit(optional)]
              if [path] is not specified, current path will be taken to analyze
            :param [is_repo] - optional. specifies that git remote repo should be ananlyzed.
            :return - json with results or json with 'error' e.g. {"error": "[text of error]"}. 
            
"""
from deepcode.src.module import deepcode_module

name = "deepcode"
description = "This package is avaliable as imported module and as cli tool. To use it as imported module, please import it and call start() method with args. To use it in terminal, just call deepcode in terminal and pass args"

# avaliable methods for module
def analyze(parent_path=None, child_path=None, is_repo=False): return deepcode_module.analyze(
    parent_path, child_path, is_repo)
