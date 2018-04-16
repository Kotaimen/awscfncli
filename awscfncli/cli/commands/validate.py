#  -*- encoding: utf-8 -*-

import click
import boto3

from ..main import cfn_cli
from ..utils import ContextObject, boto3_exception_handler, package_template, \
    is_local_path, pretty_print_stack, echo_pair, start_tail_stack_events_daemon


@cfn_cli.command()
@click.pass_context
@boto3_exception_handler
def validate(ctx):
    """Validate templates"""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():

        echo_pair(qualified_name, key_style=dict(bold=True), sep='')
        session = ctx.obj.get_boto3_session(stack_config)
        region = stack_config['Metadata']['Region']
        package = stack_config['Metadata']['Package']
        artifact_store = stack_config['Metadata']['ArtifactStore']

        client = boto3.client('cloudformation')

        if package and 'TemplateURL' in stack_config:
            template_path = stack_config.get('TemplateURL')
            if is_local_path(template_path):
                packaged_template = package_template(
                    session,
                    template_path,
                    bucket_region=region,
                    bucket_name=artifact_store,
                    prefix=stack_config['StackName'])
                stack_config['TemplateBody'] = packaged_template
                stack_config.pop('TemplateURL')

        try:
            template_body = stack_config['TemplateBody']
            result = client.validate_template(
                TemplateBody=template_body,
            )
        except KeyError:
            template_url = stack_config['TemplateURL']
            result = client.validate_template(
                TemplateURL=template_url,
            )

        click.secho('Validation complete.')
