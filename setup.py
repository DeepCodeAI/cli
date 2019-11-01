import setuptools
import os
from deepcode.src.constants.config_constants import DEEPCODE_PACKAGE_NAME

dir_name = os.path.dirname(os.path.realpath(__file__))

# parse README file for description
with open(os.path.join(dir_name, "README.md"), 'r') as readme:
    long_description = readme.read()


requirements_file = os.path.join(dir_name, "requirements.txt")
install_requires = []
with open(requirements_file) as f:
    install_requires = f.read().splitlines()

# package description should be changed from test values to final before publishing to pip
# if needed, LICENCE and README.md also can be modified
setuptools.setup(
    name=DEEPCODE_PACKAGE_NAME,
    version="0.0.1",
    author="DeepCode",
    author_email="deepcode@deepcode.com",
    description="DeepCode cli for code review",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="[TODO: add repo]",
    packages=setuptools.find_packages(),
    # dependencies
    install_requires=install_requires,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'deepcode=deepcode.command_line:cli_entry_point'
        ]
    },
    python_requires='>=3.2',
)
