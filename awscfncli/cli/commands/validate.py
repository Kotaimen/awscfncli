#  -*- encoding: utf-8 -*-

import click
import boto3

from ..main import cfn_cli
from ..utils import boto3_exception_handler, ContextObject, run_packaging
from ..utils import echo_pair, echo_pair_if_exists


@cfn_cli.command()
@click.pass_context
@boto3_exception_handler
def validate(ctx):
    """Validate templates"""
    assert isinstance(ctx.obj, ContextObject)

    for qualified_name, stack_config in ctx.obj.stacks.items():

        echo_pair(qualified_name, key_style=dict(bold=True), sep='')
        session = ctx.obj.get_boto3_session(stack_config)

        client = session.client('cloudformation')

        run_packaging(stack_config, session, ctx.obj.verbosity)

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
        echo_pair_if_exists(result, 'Capabilities', 'Capabilities')
        echo_pair_if_exists(result, 'Capabilities Reason', 'CapabilitiesReason')
        echo_pair_if_exists(result, 'Declared Transforms', 'DeclaredTransforms')
