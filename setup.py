#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs

try:
    codecs.lookup("mbcs")
except LookupError:
    ascii = codecs.lookup("ascii")
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == "mbcs"))

__version__ = "0.7.0"
URL = "https://github.com/bitshares/python-bitshares"

setup(
    name="bitshares",
    version=__version__,
    description="Python library for bitshares",
    long_description=open("README.md").read(),
    download_url="{}/tarball/{}".format(URL, __version__),
    author="Fabian Schuh",
    author_email="Fabian@chainsquad.com",
    maintainer="Fabian Schuh",
    maintainer_email="Fabian@chainsquad.com",
    url=URL,
    keywords=["bitshares", "library", "api", "rpc"],
    packages=[
        "bitshares",
        "bitsharesapi",
        "bitsharesbase",
        "bitshares.aio",
        "bitsharesapi.aio",
    ],
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Topic :: Office/Business :: Financial",
    ],
    install_requires=open("requirements.txt").readlines(),
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
    include_package_data=True,
)
