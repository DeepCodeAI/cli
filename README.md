# DeepCode's command line interface.

## Installation

Minimal supported python version is: 3.7

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

For detailed information see [development docs](development.md)


## CLI

```bash
deepcode --help

Usage: deepcode [OPTIONS] COMMAND [ARGS]...

  A tool, that detects bugs and quality issues in JavaScript, TypeScript,
  Python and Java.. It uses a mighty engine based on AI from Deepcode.

Options:
  -s, --service-url TEXT  Custom DeepCode service URL (default:
                          https://www.deepcode.ai)
  -a, --api-key TEXT      Deepcode API key
  -c, --config-file FILE  Config file (default: ~/.deepcode.json)
  --help                  Show this message and exit.

Commands:
  analyze  Analyzes your code using Deepcode AI engine.
  config   Store configuration values in a file.
  login    Initiate a new login protocal.
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
  --help                          Show this message and exit.
```

Examples:

```bash
deepcode analyze --path (<folder path one>) --path (<folder path two>) --with-linters --log-file=~/.deepcode.log -txt

deepcode analyze --path (<folder path one>) 
deepcode analyze --git-uri git@github.com:DefinitelyTyped/DefinitelyTyped.git --with-linters
```

AnalysisResults in json format as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles)

## Python native usage

DeepCode CLI can be also used as module and can be imported into another python code with python import system

To use both functions, make sure, you set an environment variable 'DEEPCODE_API_KEY' with your API KEY, that [can be obtained here](https://www.deepcode.ai/app/~platform/account)

To user self-managed instance of Deepcode, set an environment variable 'DEEPCODE_SERVICE_URL' with its user (e.g. https://example.org)

Available methods:

- analize_folders(paths, linters_enabled=False):

  ````
  :param [paths] - Paths should be a list of absolute paths to bundle dir
  :param [linters_enabled] - optional. requestes also linter analysis
  :return - dictionary with results e.g. as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles)

  example:
  deepcode.analize_folders('<path to files dir>')
  ````

- analize_git(platform, owner, repo, oid=None, linters_enabled=False):

  ````
  :param [platform] - github.com, bitbucket.org, gitlab.com.
  :param [owner] - repository account. (e.g. facebook)
  :param [repo] - repository. (e.g. react)
  :param [linters_enabled] - optional. requestes also linter analysis
  :return - dictionary with results e.g. as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles)

  example:
  deepcode.analize_git('github.com', 'facebook', 'react')
  ````
