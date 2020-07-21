# DeepCode's command line interface.

[![deepcode](https://www.deepcoded.com/api/gh/badge?key=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwbGF0Zm9ybTEiOiJnaCIsIm93bmVyMSI6IkRlZXBDb2RlQUkiLCJyZXBvMSI6ImNsaSIsImluY2x1ZGVMaW50IjpmYWxzZSwiYXV0aG9ySWQiOjczLCJpYXQiOjE1OTUzMTc1NTd9.MXYODUUN6cGSWEHQ4RSMEK7toqu-X7FDo41o4CfaMu0)](https://www.deepcoded.com/app/gh/DeepCodeAI/cli/_/dashboard?utm_content=gh%2FDeepCodeAI%2Fcli)

## Installation

Minimal supported python version is: 3.6.5

### Installation of published package from PyPI

Pip:
```bash
pip install deepcode
```

Poetry:
```bash
poetry add deepcode
```

For detailed information see [deepcode project on PYPI](https://pypi.org/project/deepcode/)

### Installation of package locally and development mode

For detailed information see [development docs](https://github.com/DeepCodeAI/cli/blob/master/docs/Development.md)


## CLI

```bash
deepcode --help

Usage: deepcode [OPTIONS] COMMAND [ARGS]...

  A tool, that detects bugs and quality issues in JavaScript, TypeScript,
  Python, Java and C/C++. It uses a mighty engine based on AI from Deepcode.

Options:
  -s, --service-url TEXT  Custom DeepCode service URL (default:
                          https://www.deepcode.ai)
  -a, --api-key TEXT      Deepcode API key
  -c, --config-file FILE  Config file (default: ~/.deepcode.json)
  --help                  Show this message and exit.

Commands:
  analyze  Analyzes your code using Deepcode AI engine.
  config   Store configuration values in a file.
  login    Initiate a new login protocol.
```


- login: this will open a browser window to log into DeepCode.
  ```bash
  deepcode login
  ```
- create/update configuration: this will walk you through some configuration steps in case you do not want to connect to
  https://www.deepcode.ai but to some other host running a DeepCode instance.
  ```bash
  deepcode config
  ```
- analyze: do analysis for a specific version of code. This will show all suggestions that are present in the code.

```
Usage: deepcode analyze [OPTIONS]

  Analyzes your code using Deepcode AI engine.

  Exit codes:
  0 - not issues found
  1 - some issues found
  2 - Execution was interrupted by the user
  3 - Some error happened while executing

Options:
  Source location: [mutually_exclusive, required]
                                  The configuration of repository location
    -p, --path DIRECTORY          Path to folder to be processed. Multiple
                                  paths are allowed
    -r, --git-uri REMOTE          Git URI (e.g.
                                  git@<platform>:<owner>/<repo>.git@<oid> or
                                  https://<platform>/<owner>/<repo>.git@<oid>)
  -l, --with-linters              Enable linters
  -log, --log-file FILE           Forward all debugging messages to a file
  -txt, --result-text             Present results in txt format
  -sev, --severity [info|warning|critical]
                                  Minimum severity level (default: info)
  --help                          Show this message and exit.
```

Examples:

```bash
deepcode analyze --path (<folder path one>) --path (<folder path two>) --with-linters --log-file=~/.deepcode.log -txt --severity warning

deepcode analyze --path (<folder path one>)
deepcode analyze --git-uri git@github.com:DefinitelyTyped/DefinitelyTyped.git --with-linters
```

AnalysisResults in json format as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles)

## Python native usage

DeepCode CLI can be also used as a module and can be imported into another python code with python import system.

To use both functions, make sure, you set an environment variable 'DEEPCODE_API_KEY' with your API KEY, that [can be obtained here](https://www.deepcode.ai/app/~platform/account)

To use self-managed instance of Deepcode, set an environment variable 'DEEPCODE_SERVICE_URL' with its user (e.g. https://example.org)

Available methods:

- analyze_folders(paths, linters_enabled=False):

  ````
  :param [paths] - Paths should be a list of absolute paths to bundle dir
  :param [linters_enabled] - optional. requests also linter analysis
  :return - dictionary with results e.g. as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles) plus: 'id' for bundle id and 'url' for online view of analysis results

  example:
  import deepcode
  deepcode.analyze_folders('<path to files dir>')
  ````

- analyze_git(platform, owner, repo, oid=None, linters_enabled=False):

  ````
  :param [platform] - github.com, bitbucket.org, gitlab.com.
  :param [owner] - repository account. (e.g. facebook)
  :param [repo] - repository. (e.g. react)
  :param [linters_enabled] - optional. requests also linter analysis
  :return - dictionary with results e.g. as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles) plus: 'id' for bundle id and 'url' for online view of analysis results

  example:
  import deepcode
  deepcode.analyze_git('github.com', 'facebook', 'react')
  ````
