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
  Required arguments:
  {path} - Path to dir for analysis or path to git repo of logged in user. Any repository that the currently logged in user has access to, can be analyzed.
  {base_path} {target_path} - paths for diff analysis. Can be either files paths or remote paths
  Remote paths should contain owner, repo and optionally commit, e.g. owner>/repo/commit
  For current files path '.' can be provided.
  Has a shortcut 'a' and options:
  -r, --remote: specifies analysis of remote
  -f, --format: results display format, supported formats: json, txt. if not specified, default format is txt
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

- analyze() - trigers

## Configuration

By default a configuration will be created in `<user_home>/.deepcodeConfig`.

## Requirements (for Ubuntu >= 16.04)

### Python >= 3.2

### Pip

```bash
sudo apt-get install python3-pip
```

### Pip dependencies

Install in virtualenv (requires additional dependency: `sudo pip3 install virtualenv`)

```bash
virtualenv venv \
source venv/bin/activate \
python3 setup.py install (for local package install)
pip3 install deepcode(for install of published package)
```

or install globally

```bash
python3 setup.py install (for local package install)
pip3 install deepcode(for install of published package)
```

## Tests

- unit tests

```bash
./test.sh
```

- python2/python3 compatibility test (requires virtualenv and pip as well as python2 and python3 installation)

```bash
./test_python2_python3_compat.sh
```
