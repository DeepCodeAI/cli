# DEEPCODE CLI DEV MODE DESCRIPTION for developers

Python >= 3.2 is required for this package

## required python packages before working/building package:

sudo python3 -m pip install --upgrade pip setuptools wheel
sudo python3 -m pip install tqdm
sudo python3 -m pip install --user --upgrade twine

if you have both python2 and python3, use python3

## descritption of cli design

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
                [-r], [--remote] - specifies analysis of git repository.
                    Must be provided before [path]. Without it [path] will be considered as files directory path
                [-f], [--format] - specifies results display format, supported formats: [json, txt]
            examples:
                deepcode analyze [path_to_files_dir] -f json  #will analyze specified path and display results in json
                deepcode analyze -r [git_username/git_repo_name] -f txt  #will analyze specified repo of logged in user and display results as readable text
optional arguments:
-h, --help            show this help message and exit
```

## package development mode with built-in hot reload

python3 setup.py develop
(how it works: the cmd runs once, after that the code can be modified and all changes will be avaliable at once)

## package local build

python3 setup.py sdist bdist_wheel

## package local install

sudo pip3 install dist/deepcode-0.0.1.tar.gz //use --upgrade after install word to update installed package

## publishing package

to publish package, please see [packaging python docs](https://packaging.python.org/tutorials/packaging-projects/)
