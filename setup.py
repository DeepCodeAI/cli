import setuptools

# parse README file for description
with open("README.md", "r") as fh:
    long_description = fh.read()

# parse requirements.txt for dependecies
with open('requirements.txt', "r") as reqs:
    required_packages = reqs.read().splitlines()


# TODO: descriptions should be changed from test values to final before publishing to pip
setuptools.setup(
    name="deepcode",
    version="0.0.1",
    author="DeepCode",
    author_email="deepcode@deepcode.com",
    description="DeepCode cli for code review",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="[TODO: add repo]",
    packages=setuptools.find_packages(),
    install_requires=required_packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'deepcode=deepcode.command_line:entry_point'
        ]
    },
    python_requires='>=3.2',
)
