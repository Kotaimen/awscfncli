# AWS CloudFormation CLI

[![Build Status](https://travis-ci.org/Kotaimen/awscfncli.svg?branch=develop)](https://travis-ci.org/Kotaimen/awscfncli)

Command Line Interface for AWS CloudFormation.

## Introduction
`awscfncli` is a simple CLI tool that helps you manage AWS CloudFormation stacks.  

Features:
- Easy to use CLI interface.
- ChangeSet support.
- Simple `YAML` stack configuration file.
- Tracking stack events.

<img alt="Sample" src="https://s3.amazonaws.com/stonemason/cdn/dist/awscfncli/changeset-execute-demo-01.gif">

Usage:
    
    cfn COMMAND SUBCOMMAND STACK_CONFIG [ARGS]...

To view a list of available subcommands, type:

    cfn COMMAND --help

To view help of a particular subcommand, type:
    
    cfn COMMAND SUBCOMMAND --help


`STACK_CONFIG` is a simple `YAML` file descripbes stack deploy parameters:

```yaml

Stack:
  Region:               us-east-1
  StackName:            SampleIAMUsersGroupsAndPolicies
  TemplateURL:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
  Capabilities:         [CAPABILITY_IAM]
  Parameters:
    Password:           bob180180180
  Tags:
    project:            Bob
```

## Install

Install `awscfncli` using [pip](https://pip.pypa.io/):

    pip install awscfncli

The package itself is runnable as a module: 

    python -m awscfncli 

## Tutorial

Read the tutorial [here](https://kotaimen.github.io/awscfncli/)

## AWS Credentials

Check `boto3` configution document [here](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration).
