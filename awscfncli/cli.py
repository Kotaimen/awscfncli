#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

import click
import boto3
import pkg_resources

MODULE_NAME = 'awscfncli'
VERSION = pkg_resources.require(MODULE_NAME)[0].version


@click.group()
@click.pass_context
@click.version_option(version=VERSION)
@click.option('--profile', type=click.STRING,
              default=None,
              help='Use a specific profile from your credential file.')
def cfn(ctx, profile):
    """Welcome to the CloudFormation Stack Management Command Line Interface."""
    ctx.obj = dict()

    session = boto3.session.Session(profile_name=profile)
    ctx.obj['session'] = session


@cfn.group()
@click.pass_context
def stack(ctx):
    """CloudFormation Stack commands"""
    pass


@cfn.group()
@click.pass_context
def template(ctx):
    """CloudFormation Template commands"""
    pass


@cfn.group()
@click.pass_context
def changeset(ctx):
    """CloudFormation ChangeSet commands"""
    pass
