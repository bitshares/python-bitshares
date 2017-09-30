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

VERSION = '0.1.8'

setup(
    name='bitshares',
    version=VERSION,
    description='Python library for bitshares',
    long_description=open('README.md').read(),
    download_url='https://github.com/xeroc/python-bitshares/tarball/' + VERSION,
    author='Fabian Schuh',
    author_email='Fabian@chainsquad.com',
    maintainer='Fabian Schuh',
    maintainer_email='Fabian@chainsquad.com',
    url='http://www.github.com/xeroc/python-bitshares',
    keywords=['bitshares', 'library', 'api', 'rpc'],
    packages=[
        "bitshares",
        "bitsharesapi",
        "bitsharesbase"
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
    install_requires=[
        "graphenelib>=0.5.3",
        "websockets",
        "appdirs",
        "Events",
        "scrypt",
        "pycryptodome",  # for AES, installed through graphenelib already
    ],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    include_package_data=True,
)
