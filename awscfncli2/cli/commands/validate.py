#  -*- encoding: utf-8 -*-

import click

from ..main import cfn_cli
from ..utils import command_exception_handler
from ..utils import echo_pair_if_exists
from ...cli import ClickContext


@cfn_cli.command()
@click.pass_context
@command_exception_handler
def validate(ctx):
    """Validate templates"""
    assert isinstance(ctx.obj, ClickContext)

    for stack_context in ctx.obj.runner.contexts:
        stack_context.make_boto3_parameters()

        ctx.obj.ppt.pprint_stack_name(
            stack_context.stack_key,
            stack_context.parameters['StackName'],
            'Validating '
        )

        session = stack_context.session
        client = session.client('cloudformation')

        stack_context.run_packaging()

        try:
            template_body = stack_context.parameters['TemplateBody']
            result = client.validate_template(
                TemplateBody=template_body,
            )
        except KeyError:
            template_url = stack_context.parameters['TemplateURL']
            result = client.validate_template(
                TemplateURL=template_url,
            )

        click.secho('Validation complete.')
        echo_pair_if_exists(result, 'Capabilities', 'Capabilities')
        echo_pair_if_exists(result, 'Capabilities Reason', 'CapabilitiesReason')
        echo_pair_if_exists(result, 'Declared Transforms', 'DeclaredTransforms')
