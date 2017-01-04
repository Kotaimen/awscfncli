# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '03/01/2017'

from setuptools import setup, find_packages

setup(
    name='awscfncli',
    version='0.1',
    description='AWS CloudFormation CLI',
    author='Kotaimen',
    author_email='kotaimen.c@gmail.com',
    url='https://github.com/Kotaimen/awscfncli',
    license='MIT',
    install_requires=[
        'six>=1.10.0',
        'boto3>=1.3',
        'click>=6.0',
        'PyYAML>=3.11',
    ],
    packages=find_packages(exclude=('tests',)),
    entry_points='''
        [console_scripts]
        cfn=awscfncli.cli:cli
    ''',
)
