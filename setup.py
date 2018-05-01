# -*- encoding: utf-8 -*-

import os
from setuptools import setup, find_packages

__author__ = 'kotaimen'
__date__ = '22-Feb-2018'

here = os.path.abspath(os.path.dirname(__file__))

long_description = """

AWS CloudFormation CLI
**********************

Introduction
============

``awscfncli`` AWS CloudFormation stack management command line interface.

Features:

* awscli a-like CLI interface.
* Simple YAML stacks configuration file.
* Tracking stack events in the CLI.
* Managing stacks across different stages and accounts.

"""

install_requires = [
    'six>=1.10.0',
    'boto3>=1.6',
    'botocore>=1.9',
    'click>=6.0',
    'PyYAML>=3.11',
    'jsonschema>=2.6.0',
    'awscli>=1.14'
]

test_requires = ['pytest', 'pytest-cov', 'mock']

dev_requires = test_requires

setup(
    # Project Name
    name='awscfncli2',

    # Version and description
    version='2.0.0-rc2',
    description='AWS CloudFormation CLI',
    long_description=long_description,

    # Author details
    author='Kotaimen, Ray',
    author_email='kotaimen.c@gmail.com, gliese.q@gmail.com',

    # Project home
    url='https://github.com/Kotaimen/awscfncli',

    # License detail
    license='MIT',

    # Classification and Keywords
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',

        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        'Development Status :: 5 - Production/Stable',

        'Natural Language :: English',

        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
    keywords='awscfncli awscfncli2 aws cfn cli cloudformation stack '
             'template changeset commandline development',

    packages=find_packages(exclude=['tests.*', 'tests']),
    install_requires=install_requires,
    extras_require={
        'test': test_requires,
        'dev': dev_requires
    },

    entry_points='''
        [console_scripts]
        cfn-cli=awscfncli2.__main__:main
    ''',
)
