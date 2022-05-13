#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

__version__ = "0.7.1"

setup(
    version=__version__,
    install_requires=open("requirements.txt").readlines(),
    tests_require=open("requirements-test.txt").readlines(),
    include_package_data=True,  # needed for data from manifest
    # Use git repo data (latest tag, current commit hash, etc) for building a
    # version number according PEP 440. Conflicts with semantic-release
    setuptools_git_versioning={
        "enabled": False,
    },
)
