# DEEPCODE CLI DEV MODE DESCRIPTION for developers

<!-- TODO: modify this while developing -->

## required python packages before working/building package:

sudo python -m pip install --upgrade pip setuptools wheel
sudo python -m pip install tqdm
sudo python -m pip install --user --upgrade twine

## descritption of cli design

after install/start dev mode, cli is avaliable in terminals by calling 'deepcode'.
cli accepts commands in format [cli_name][cmd_name], e.g. deepcode login
the list of commands will be avaliable later

<!-- TODO: list of commands -->

## package development mode with built-in hot reload

python3 setup.py develop
(how it works: the cmd runs once, after that the code can be modified and all changes will be avaliable at once)

## package local build

python3 setup.py sdist bdist_wheel

## package local install

sudo pip3 install dist/testpkg-0.0.1.tar.gz //use --upgrade after install word to update installed package
