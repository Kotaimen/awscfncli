# AWS CloudFormation CLI

The missing AWS CloudFormation CLI

## Introduction

`awscfncli` helps build and manage AWS CloudFormation stacks. 

Features:

- Manage stacks in different accounts & regions in a single YAML config file.
- Organize stack using stages and blueprints. 
- Select stacks to operate on using globs.
- Cross-stack parameter reference.
- Automatically package and upload template resources.
- Push button SAM deployment using `stack sync` command.
- Display and tracking stack events in the CLI.
- List stack resources, outputs and exports in the CLI.
 
## Install

Install using [pip](https://pip.pypa.io/) from 
[pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli2

To enable click supported auto-complete, add following line to `.bachrc`
    
    eval "$(_CFN_CLI_COMPLETE=source cfn-cli)"

## TBD...
