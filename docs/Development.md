### DEEPCODE CLI development mode description for developers

Python >= 3.6 is required for this package
If you have an older version, please consider using [pyenv](https://realpython.com/intro-to-pyenv/) to manage different python versions.

### Environment setup

Package can be developed/built with Poetry:

Install poetry, dependencies and activate virtual environment:
```bash
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python
```

Add a following line to your shell specific config file (~/.bashrc, ~/.zshrc):
```bash
export PATH="$HOME/.poetry/bin:$PATH"
```

For more details refer to [Poetry documentation](https://python-poetry.org/docs/)

### Create virtual environment
```bash
poetry shell
```

(OPTIONAL) If you prefer to have all dependencies in the same place together with your code, create a virtualenv manually:
```bash
virtualenv ./venv --python python3
source ./venv/bin/activate
```

Troubleshooting: Make sure that your user has full rights to user folder with all subfolders

### Install dependencies
```bash
poetry install
```

## Description of cli options

```bash
poetry run deepcode --help
```

## Module mode

CLI can work as command line interface and as imported module.
To read more about module mode, see [readme docs](README.md)

## Package build

Go to pyproject.toml and increment version.

```bash
poetry build
```

### Publishing

```bash
poetry publish
```

### Tests

Run tests:

```bash
poetry run pytest tests
```
