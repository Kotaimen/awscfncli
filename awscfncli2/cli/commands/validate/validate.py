import click

from awscfncli2.cli.context import Context
from awscfncli2.cli.utils.deco import command_exception_handler
from awscfncli2.cli.utils.pprint import echo_pair_if_exists


@click.command('validate')
@click.pass_context
@command_exception_handler
def cli(ctx):
    """Validate template file."""
    assert isinstance(ctx.obj, Context)

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
