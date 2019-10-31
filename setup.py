import setuptools
from deepcode.src.constants.config_constants import DEEPCODE_PACKAGE_NAME

# parse README file for description
with open("README.md", "r") as readme:
    long_description = readme.read()

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
    install_requires=[
        'certifi==2019.3.9',
        'chardet==3.0.4',
        'futures==3.1.1',
        'httpretty==0.9.6',
        'idna==2.8',
        'progressbar2==3.39.3',
        'python-utils==2.3.0',
        'requests==2.21.0',
        'requests-futures==1.0.0',
        'six==1.12.0',
        'urllib3==1.24.3'
    ],
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
