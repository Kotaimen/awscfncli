#  -*- encoding: utf-8 -*-

import click
from . import stack
from ..utils import ContextObject
from ..utils import boto3_exception_handler
from ..utils import pretty_print_stack
from ..utils import start_tail_stack_events_daemon
from ..utils import package_template, is_local_path


@stack.command()
@click.option('--no-wait', is_flag=True, default=False,
              help='Exit immediately after operation is started.')
@click.option('--on-failure',
              type=click.Choice(['DO_NOTHING', 'ROLLBACK', 'DELETE']),
              default=None,
              help='Determines what action will be taken if stack creation '
                   'fails. This must be one of: DO_NOTHING, ROLLBACK, or '
                   'DELETE. Note setting this option overwrites "OnFailure" '
                   'and "DisableRollback" in the stack configuration file.')
@boto3_exception_handler
@click.pass_context
def deploy(ctx, no_wait, on_failure):
    """Deploy a new stack"""
    assert isinstance(ctx.obj, ContextObject)

    for stack_config in ctx.obj.stacks:
        click.secho(
            'Deploying stack %s.%s' % \
            (stack_config['Metadata']['StageName'], stack_config['StackName']),
            bold=True)
        deploy_one(ctx, stack_config, no_wait, on_failure)


def deploy_one(ctx, stack_config, no_wait, on_failure):
    session = ctx.obj.get_boto3_session(stack_config)
    region = stack_config['Metadata']['Region']
    package = stack_config['Metadata']['Package']
    artifact_store = stack_config['Metadata']['ArtifactStore']

    # option handling
    if on_failure is not None:
        stack_config.pop('DisableRollback', None)
        stack_config['OnFailure'] = on_failure

    # connect to cloudformation
    cloudformation = session.resource(
        'cloudformation',
        region_name=region)

    # pop metadata form stack config
    stack_config.pop('Metadata')

    # package the template
    if package and 'TemplateURL' in stack_config:
        template_path = stack_config.get('TemplateURL')
        if not is_local_path(template_path):
            packaged_template = package_template(
                session,
                template_path,
                bucket_region=region,
                bucket_name=artifact_store,
                prefix=stack_config['StackName'])
            stack_config['TemplateBody'] = packaged_template
            stack_config.pop('TemplateURL')

    # create stack
    if ctx.obj.verbosity > 0:
        click.echo(stack_config)
    stack = cloudformation.create_stack(**stack_config)
    stack_id = stack.stack_id
    pretty_print_stack(stack)

    # exit immediately
    if no_wait:
        return

    # start event tailing
    start_tail_stack_events_daemon(session, stack, latest_events=0)

    # wait until update complete
    waiter = session.client('cloudformation', region_name=region). \
        get_waiter('stack_create_complete')
    waiter.wait(StackName=stack_id)

    click.secho('Stack deployment complete.', fg='green')
