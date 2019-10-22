from .src.main import main
# The code and varialbles above will be avaliable when importing package to another python file as package
name = "deepcode"
description = "This package is avaliable as imported module and as cli tool. To use it as imported module, please import it and call start() method with args. To use it in terminal, just call deepcode in terminal and pass args"
# TODO: make method in src/main.py to work with args
start = main
