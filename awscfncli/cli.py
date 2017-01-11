#!/usr/bin/env python
#  -*- encoding: utf-8 -*-

from __future__ import with_statement

"""Simple CloudFormation Stack Management Tool"""

import click


@click.group()
@click.pass_context
@click.version_option()
def cli(ctx):
    """Welcome to the CloudFormation Stack Management Command Line Interface."""
    ctx.obj = dict()


@cli.group()
@click.pass_context
def stack(ctx):
    """CloudFormation Stack commands"""
    pass


@cli.group()
@click.pass_context
def template(ctx):
    """CloudFormation Template commands"""
    pass


@cli.group()
@click.pass_context
def changeset(ctx):
    """CloudFormation Changeset commands"""
    pass

