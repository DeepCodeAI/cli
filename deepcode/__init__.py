"""
DeepCode module for analyzing code.
Avaliable methods:
  analyze([parent_path: string], [child_path:string], [is_repo: boolean]): -> return json
"""
from deepcode.src.module import deepcode_module

name = "deepcode"
description = "This package is avaliable as imported module and as cli tool. To use it as imported module, please import it and call avaliable methods with args. To use it in terminal, just call deepcode in terminal and pass args"

# avaliable methods for module


def analyze(parent_path=None, child_path=None, is_repo=False):
    '''
    analyze([parent_path: string], [child_path:string], [is_repo: boolean]): -> return json\n
      Paths can be absolute path to bundle dir or path to remote repo of current registered user e.g.[user_name]/[repo_name]/[commit(optional)]\n
      :param [parent_path] - if [parent_path] is not specified, current path will be taken to analyze\n
      :param [child_path] - optional. Used for diff analysis. If specifed, diff analysis of two bundles will start\n
      :param [is_repo] - optional. specifies that git remote repo should be ananlyzed.\n
      :return - json with results e.g. {'files':{}, 'suggestions':{}} or json with error e.g. {"error": "[text of error]"}.\n
      example:\n
        deepcode.analyze('<owner/repo_name/commit>', is_repo=True) #analysis for remote bundle\n
        deepcode.analyze('<path to files dir>') # analysis for files\n
        deepcode.analyze() #analysis of current folder of file\n
    '''
    return deepcode_module.analyze(
        parent_path, child_path, is_repo)
