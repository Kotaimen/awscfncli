"""Main cli entry point, called when run as a package."""

__author__ = 'kotaimen'
__date__ = '28-Feb-2018'

from .cli.main import cli


def main():
    """CLI Entry point when run as module"""
    cli(
        auto_envvar_prefix='CFN',
        prog_name='cfn-cli'
    )


if __name__ == '__main__':
    main()
