# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '28-Feb-2018'

"""Main cli entry point, called when awscfncli run as a package, which is 
imported in setuptools intergration.

cli package structure:

    Click main entry:
        cli/main.py
    
    Commands:
        cli/commands/<command_name>.py
        
    Command groups:
        cli/<group_name>/__init__.py
    
    Subcommands:   
        cli/<group_name>/command_name.py

All commands are imported in cli/__init__.py to get registered into click. 
"""

from .cli import cfn_cli


def main():
    cfn_cli(
        auto_envvar_prefix='CFN'
    )


if __name__ == '__main__':
    main()
