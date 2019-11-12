"""Dynamic Autocomplete helpers"""
import click
import click_completion.core

from awscfncli2.config import find_default_config, load_config, ConfigError


def profile_auto_complete(ctx, args, incomplete):
    """Autocomplete for --profile

    Lists any profile name contains given incomplete.
    """
    import boto3
    profiles = boto3.session.Session().available_profiles
    return sorted(p for p in profiles if incomplete in p)


def stack_auto_complete(ctx, args, incomplete):
    """Autocomplete for --stack

    By default, returns qualified names start with qualified stack

    """
    import argparse
    # use argparse to extract config file name
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default=None)
    (namespace, remain) = parser.parse_known_args(args)
    config_filename = find_default_config(namespace.file)

    try:
        deployments = load_config(config_filename)
    except ConfigError as e:
        # ignore any config parsing errors
        return list()

    # get a sorted list of qualified names

    stack_names = sorted(
        d.stack_key.qualified_name for d in deployments.query_stacks())

    # remove meta chars
    incomplete = incomplete.lower().translate({'*': '', '?': ''})
    return list(
        (s.stack_key.qualified_name, s.parameters.StackName) for s in deployments.query_stacks()
        if s.stack_key.qualified_name.lower().startswith(incomplete)
    )


def install_callback(ctx, attr, value):
    if not value or ctx.resilient_parsing:
        return value
    shell, path = click_completion.core.install()
    click.echo(f'{shell} completion installed in {path}')
    exit(0)
