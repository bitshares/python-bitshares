#!/usr/bin/env python3

from setuptools import setup

# Work around mbcs bug in distutils.
# http://bugs.python.org/issue10945
import codecs
try:
    codecs.lookup('mbcs')
except LookupError:
    ascii = codecs.lookup('ascii')
    codecs.register(lambda name, enc=ascii: {True: enc}.get(name == 'mbcs'))

VERSION = '0.1.10'

setup(
    name='python-utransnet',
    version=VERSION,
    description='Python library for transnet',
    long_description=open('README.md').read(),
    download_url='https://github.com/u-transnet/python-utransnet/tarball/' + VERSION,
    author='Fabian Schuh',
    author_email='Fabian@chainsquad.com',
    maintainer='Ilya Shmelev',
    maintainer_email='ishmelev23@gmail.com',
    url='http://www.github.com/u-transnet/python-transnet',
    keywords=['transnet', 'library', 'api', 'rpc'],
    packages=[
        "transnet",
        "transnetapi",
        "transnetbase"
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Topic :: Office/Business :: Financial',
    ],
    dependency_links=[
        'git+https://github.com/u-transnet/python-graphenelib.git@0.5.4-utt#egg=graphenelib'
    ],
    install_requires=[
        "graphenelib",
        "websockets",
        "appdirs",
        "Events",
        "scrypt",
        "pycryptodome"  # for AES, installed through graphenelib already
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
