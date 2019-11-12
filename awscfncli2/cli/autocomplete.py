"""Dynamic Autocomplete helpers"""

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


    """
    import argparse
    # use argparse to extract config file name
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', '-f', default=None)
    (namespace, remain) = parser.parse_known_args(args)
    config_filename = find_default_config(namespace.file)

    try:
        deployments = load_config(config_filename)
    except ConfigError:
        # ignore any config parsing errors
        return

    # get a sorted list of qualified names
    stack_names = sorted(
        d.stack_key.qualified_name for d in deployments.query_stacks('*'))

    # remove meta chars
    incomplete = incomplete.lower().translate({'*': '', '?': ''})
    return list(s for s in stack_names if s.lower().startswith(incomplete))
