#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup

__version__ = '0.1-dev'

meta = dict(
    name='sartoris',
    version=__version__,
    description='Tool to manage using git as a deployment management tool',
    long_description='Tool to manage using git as a deployment \
    management tool',
    author="Wikimedia Foundation",
    author_email="info@wikimedia.org",
    url='https://github.com/wikimedia/sartoris',
    packages=['sartoris'],
    entry_points={'console_scripts': ['sartoris = sartoris:cli']},
    install_requires=['dulwich'],
    keywords=['git', 'deploy', 'scripts', 'cli'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities"
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "License :: OSI Approved :: MIT License",
    ],
    zip_safe=False,
    license="License :: OSI Approved :: BSD License",
)

# Automatic conversion for Python 3 requires distribute.
if False and sys.version_info >= (3,):
    meta.update(dict(
        use_2to3=True,
    ))

setup(**meta)
