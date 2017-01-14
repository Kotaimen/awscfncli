#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

import click
import pkg_resources

MODULE_NAME = 'awscfncli'
VERSION = pkg_resources.require(MODULE_NAME)[0].version


@click.group()
@click.pass_context
@click.version_option(version=VERSION)
def cfn(ctx):
    """Welcome to the CloudFormation Stack Management Command Line Interface."""
    ctx.obj = dict()


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
