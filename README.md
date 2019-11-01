# CLI

DeepCode's command line interface.

## Usage

- login: this will open a browser window to log into DeepCode.
  ```bash
  deepcode login
  ```
- logout: logout from cli
  ```
  deepcode logout
  ```
- create/update configuration: this will walk you through some configuration steps in case you do not want to connect to
  https://www.deepcode.ai but to some other host running a DeepCode instance.
  Has a shortcut 'c' and options -f, --format to display current config. Supported formats: json, txt
  ```bash
  deepcode config
  ```
  list current config in json or text format. Examples:
  ```
  deepcode config -f json
  deepcode c -f txt
  ```
- analyze: do analysis for a specific version of code. This will show all suggestions that are present in the code.

```
Required arguments:
 {path} - Path to dir for analysis or path to git repo of logged in user. Any repository that the currently logged in user has access to, can be analyzed.
 {base_path} {target_path} - paths for diff analysis. Can be either files paths or remote paths
 Remote paths should contain owner, repo and optionally commit, e.g. owner>/repo/commit
 For current files path '.' can be provided.
 Has a shortcut 'a' and options:
 -r, --remote: specifies analysis of remote
 -s, --silent: if provided, cli progressbars will be hidden
 -f, --format: results display format, supported formats: json, txt. if not specified, default format is txt
```

Examples:

```bash
deepcode analyze (<folder path>) --format json
deepcode a (<folder path>) -f json
deepcode a . -f txt (alayze current folder and show results as text)
deepcode a -r (<owner>/<repo> | <owner>/<repo>/<commit>) -f txt
deepcode a -r (<owner>/<repo>) (<owner>/<repo>/<commit>) -f json #diff analysis of remote bundles
deepcode a (<folder path>) (<folder path>) # diff analysis of folders

```

AnalysisResults in json format as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles)

## CLI as module

Deepcode CLI can be also used as module and can be imported into another python code with python import system
CLI module mode avaliable methods:

- analyze(parent_path: string, child_path: string, is_repo: boolean): json object

  ````
  Paths can be absolute path to bundle dir or path to remote repo of current registered user e.g.[user_name]/[repo_name]/[commit(optional)]
  :param [parent_path] - if [parent_path] is not specified, current path will be taken to analyze
  :param [child_path] - optional. Used for diff analysis. If specifed, diff analysis of two bundles will start
  :param [is_repo] - optional. specifies that git remote repo should be ananlyzed.
  :return - json with results e.g. {'files':{}, 'suggestions':{}} or json with error e.g. {"error": "[text of error]"}.

  example:
  deepcode.analyze('<owner/repo_name/commit>', is_repo=True) #analysis for remote bundle
  deepcode.analyze('<path to files dir>') # analysis for files
  deepcode.analyze() #analysis of current folder of file```
  ````

## Configuration

By default a configuration will be created in `<user_home>/.deepcodeConfig`.

## Requirements (for Ubuntu >= 16.04)

### Python >= 3.2

### Pip

```bash
sudo apt-get install python3-pip
```

### Installation of package locally and development mode

For detailed information see [development docs](Development.md)

### Installation of published package from PyPI

Install in virtualenv (requires additional dependency: `sudo pip3 install virtualenv`)

```bash
virtualenv venv
source venv/bin/activate
pip3 install deepcode
```

or install globally

```bash
python3 setup.py install (for local package install)
pip3 install deepcode
```
