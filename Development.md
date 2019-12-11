### DEEPCODE CLI development mode description for developers

Python >= 3.4 is required for this package

### Virtual environment

Package can be developed/built with python virtualenv:

Install in virtualenv (requires additional dependency: `sudo pip3 install virtualenv`)
Start virtualenv:

```bash
virtualenv venv
source venv/bin/activate
```

After that, develop and build bash commands are exactly the same as for global develop/install

### Required python packages before working/building package:

```bash
sudo python3 -m pip install --upgrade pip setuptools wheel
sudo python3 -m pip install tqdm
sudo python3 -m pip install --user --upgrade twine
```

if you have both python2 and python3, use python3

### Installing requirements and setup:

```bash
sudo -H pip3 install -r ./requirements.txt
```

## Package development mode with built-in hot reload

```bash
sudo -H python3 setup.py develop
```

to remove the package again:

```
sudo -H python3 setup.py develop -u
```

Note that clashes with pip3-installed packages are possible. To make sure the deepcode command
invokes development code with hot reloading, it is apparently necessary to do:

```
sudo pip3 uninstall deepcode
```

(how it works: the cmd runs once, after that the code can be modified and all changes will be avaliable at once)

## Descritption of cli options

```
after install/start dev mode, cli is avaliable in terminal by calling 'deepcode'.

usage: deepcode [command] [command argument] [-option] [option_argument]

positional arguments:
login       Login to DeepCode CLI using GitHub or BitBucket account
logout      Logout from CLI
config (c)  Configure Deepcode CLI backend host. Without options will provide steps to configure CLI.
            shortcuts: c
            options: [-f], [--format] - specifies results display format, supported formats: [json, txt]
            example:
                deepcode config -f txt #will display cli config in txt foromat
analyze (a) Command to analyze code.
            shortcuts: a
            required: [path] - should be provided to specify the path to analyze.
                [path] can be absolute path to files directory,
                or path to git repo from GitHub/BitBucket account of logged in user, e.g.[git_username]/[git_repo_name]/[commit(optional)]
            options:
                [-r], [--remote] - if specified, analyzes git repository
                [-s], [--silent] - if specified, cli progressbar will be hidden
                [-f], [--format] - specifies results display format, supported formats: [json, txt]
            examples:
                deepcode analyze [path_to_files_dir] -f json  #will analyze specified path and display results in json
                deepcode analyze -r [git_username/git_repo_name] -f txt  #will analyze specified repo of logged in user and display results as readable text
optional arguments:
-h, --help            show this help message and exit
```

## Module mode

CLI can work as command line interface and as imported module.
To read more about module mode, see [readme docs](README.md)

## Package local build

```bash
python3 setup.py sdist bdist_wheel
```

## Package local install

```bash
sudo pip3 install dist/deepcode-0.0.1.tar.gz
sudo pip3 install --upgrade dist/deepcode-0.0.1.tar.gz // to update installed package
```

IMPORTANT! Before installing package locally, please make sure, that package was removed from dev mode,
to uninstall dev mode use:

```bash
python setup.py develop -u
```

Otherwise, you might get import errors or other errors because of conflicts of package both in dev and prod modes

### Publishing

Before publishing setup.py should be modified and package info should be added for production build

For more info about develop and publish packages, please see [packaging python docs](https://packaging.python.org/tutorials/packaging-projects/)

### Tests

Run tests:

```bash
./test.sh
```
