# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '20/01/2017'

import os
import click
import json
import yaml

from ..utils import boto3_exception_handler, echo_pair
from ...cli import template


@template.command()
@click.argument('stack_name')
@click.argument('config_file',
                type=click.Path(dir_okay=False, writable=True))
@click.argument('template_file', required=False, default=None,
                type=click.Path(dir_okay=False, writable=True))
@click.option('--region', help='AWS region.')
@click.option('--template-format', default='JSON',
              type=click.Choice(['YAML', 'JSON']),
              help='Format of the template file, must be YAML or JSON, default '
                   'is JSON.')
@click.option('--indent', is_flag=True, default=False,
              help='Indent generated template file (only applies to JSON '
                   'format).')
@click.option('--overwrite', is_flag=True, default=False,
              help='Indent generated template file (only applies to JSON '
                   'format).')
@click.pass_context
@boto3_exception_handler
def reflect(ctx, stack_name, config_file, template_file,
            region, template_format, indent, overwrite):
    """Generate awscfncli configuration file from an existing stack.

    Template retried from CloudFormation service may be different from the
    original.   And if template is larger than 51200 bytes, generated
    configuration will fail to deploy, please use S3 and TemplateURL instead.

    \b
    STACK_NAME          Name of the stack.
    CONFIG_FILE         Generated tack configuration file.
    TEMPLATE_FILE       Generated stack template file.
    """
    session = ctx.obj['session']

    click.echo('Inspecting stack...')
    echo_pair('Region', region)
    echo_pair('Stack', stack_name)

    config = dict()
    config['Region'] = region
    config['StackName'] = stack_name

    client = session.client('cloudformation', region_name=region)
    r = client.get_template(StackName=stack_name)

    # write template
    if template_file is None:
        template_file = '.'.join([stack_name, template_format.lower()])

    if os.path.exists(template_file):
        if not overwrite:
            click.secho('"%s" already exists, overwrite using --overwrite.' \
                        % template_file, fg='red')
            return 1

    with open(template_file, 'w') as fp:
        if template_format == 'JSON':
            json.dump(r['TemplateBody'], fp, indent=(2 if indent else None))
        elif template_format == 'YAML':
            yaml.safe_dump(r['TemplateBody'], fp)
        else:
            assert False
        click.secho('Saved template to "%s"' % template_file, fg='green')

    config['TemplateBody'] = template_file

    cfn = session.resource('cloudformation', region_name=region)
    stack = cfn.Stack(stack_name)

    if stack.capabilities:
        config['Capabilities'] = stack.capabilities
    if stack.role_arn:
        config['RoleARN'] = stack.role_arn

    if stack.parameters:
        config['Parameters'] = \
            dict((p['ParameterKey'], p['ParameterValue']) for p in
                 stack.parameters)

    if stack.tags:
        config['Tags'] = \
            dict((t['Key'], t['Value']) for t in stack.tags)

    if os.path.exists(config_file):
        if not overwrite:
            click.secho('"%s" already exists, overwrite using --overwrite.' \
                        % config_file, fg='red')
            return 1

    with open(config_file, 'w') as fp:
        yaml.safe_dump(dict(Stack=config), fp, default_flow_style=False)
        click.secho('Generated config "%s"' % config_file, fg='green')
