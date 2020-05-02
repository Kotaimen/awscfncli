# -*- encoding: utf-8 -*-

import os

from setuptools import setup, find_packages

__author__ = 'kotaimen'
__date__ = '22-Feb-2018'

here = os.path.abspath(os.path.dirname(__file__))

long_description = open('README.md').read()

install_requires = [
    'botocore',
    'boto3',
    'awscli',
    'click~=7.0',
    'click_completion==0.5.2',
    'PyYAML<5.3,>=3.10', # Fix ERROR: awscli xxx has requirement PyYAML<5.3,>=3.10 , but you'll have pyyaml 5.3 which is incompatible.
    'jsonschema>=2.6.0',
    'backoff'
]

setup(
    # Project Name
    name='awscfncli2',

    # Version and description
    version='3.0.0',
    description='AWS CloudFormation CLI',
    long_description=long_description,
    long_description_content_type='text/markdown',

    # Author details
    author='Kotaimen, Ray',
    author_email='kotaimen.c@gmail.com, gliese.q@gmail.com',

    # Project home
    url='https://github.com/Kotaimen/awscfncli',

    # License detail
    license='MIT',

    # Classification and Keywords
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
    keywords='aws cfn cli awscfncli cloudformation changeset sam serverless',
    python_requires='>=3.6',
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
