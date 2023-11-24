# -*- encoding: utf-8 -*-

import os

from setuptools import setup, find_packages

__author__ = 'andyfase'
__date__ = '23-Nov-2023'

# here = os.path.abspath(os.path.dirname(__file__))

long_description = open('README.md').read()

install_requires = [
    'backoff>2.2',
    'boto3>1.29',
    'botocore>1.32',
    'click>8',
    'click-completion>0.5',
    'colorama>0.4',
    'jsonschema>4',
    'pyyaml>6',
    's3transfer>=0.7'
]

setup(
    # Project Name
    name='cfncli',

    # Version and description
    version='0.0.5',
    description='CloudFormation CLI Wrapper',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # Author details
    author='Fase, Andy',
    author_email='andyfase@gmail.com',

    # Project home
    url='https://github.com/andyfase/cfncli',

    # License detail
    license='MIT',

    # Classification and Keywords
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
    keywords='aws cfn cli cloudformation changeset sam serverless',
    python_requires='>=3.7',
    packages=find_packages(exclude=['tests.*', 'tests']),
    package_data={
        'awscfncli2.config': ['*.json', '*.yaml']
    },
    install_requires=install_requires,
    entry_points='''
    [console_scripts]
    cfn-cli=awscfncli2.__main__:main
    ''',
)
