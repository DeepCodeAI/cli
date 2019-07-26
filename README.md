# CLI

DeepCode's command line interface.

## Usage
- log in: this will open a browser window to log into DeepCode.
  ```bash
  python main.py login
  ```
- create/update configuration: this will walk you through some configuration steps in case you do not want to connect to
 https://www.deepcode.ai but to some other host running a DeepCode instance.
  ```bash
  python main.py config
  ```
- analyze: do an audit for a specific version of code. This will show all suggestions that are present in the code.
  ```bash
  python main.py analyze (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>)
  ```
  Examples:
  ```bash
  python main.py analyze <path_to_some_local_folder>
  python main.py analyze eclipse/che
  python main.py analyze eclipse/che/08708f0f9a19d121b51af1741b8b5094fe38048b
  ```
- diff: compare to versions of code. This will show all suggestions that were introduced with a code change.
  The `<current>` code will be compared to the `<base>` code and only suggestions will be shown that were not present in
  `<base>` but are present in `<current>`.
  ```bash
  python main.py diff <base> <current>
        # where  <base> = (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>)
        # and <current> = (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>)
  ```
- logout
  ```bash
  python main.py logout
  ```
- show help
  ```bash
  python main.py --help
  ```

Optinal arguments:
- `-c <config_json>` path to config file, default is `<user_home>/.deepcodecli`
- `--json` output results in json format to stdout, see json mode below

## json mode

- login
  ```bash
  python main.py login --json
  ```
  Response:
  - in case the user is logged in already (no user action required):
  ```
  {
    "loggedIn": true,
    "userType": "private" | "public"
  }
  ```
  - in case the user needs to log in:
  ```
  {
    "loggedIn": false,
    "loginURL": string (uri)
  }
  ```
- wait for login: This can be used to wait until the user login succeeded.
  The command will exit once the user is logged in.
  ```bash
  python main.py wait_for_login --json
  ```
- analyze
  ```bash
  python main.py analyze (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>) --json
  ```
  Response: *analysisResults* in json format as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles).
- diff
  ```bash
  python main.py diff <base> <current> --json
        # where  <base> = (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>)
        # and <current> = (<folder> | <owner>/<repo> | <owner>/<repo>/<commit>)
  ```
  Response: *analysisResults* in json format as described [here](https://www.deepcode.ai/docs/REST%20APIs%2FBundles).
- logout
  ```bash
  python main.py logout --json
  ```
  The command will exit once the user is logged out.

## Configuration

Required parameters in json config file:
- dc_server_host
- dc_server_port

An example configuration can be found in `example_config.json`.
By default a configuration will be created in `<user_home>/.deepcodecli`.

## Requirements (for Ubuntu 18.04)
### Pip
```bash
sudo apt-get install python-pip
```

### Pip dependencies
Install in virtualenv (requires additional dependency: `sudo pip install virtualenv`)
```bash
virtualenv venv \
source venv/bin/activate \
pip install -r requirements.txt
```
or install globally
```bash
sudo pip install -r requirements.txt
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
