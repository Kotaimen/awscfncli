# AWS CloudFormation CLI

[![Build Status](https://travis-ci.org/Kotaimen/awscfncli.svg?branch=develop)](https://travis-ci.org/Kotaimen/awscfncli)

Command Line Interface for AWS CloudFormation.

## Introduction
`awscfncli` is a simple CLI tool that helps you manage AWS CloudFormation stacks.  

Features:

- Simple CLI interface.
- `YAML` stack configuration file.
- Stack management.
- ChangeSet management.
- Display and tracking stack events, including nested stack.
- Tracking stack export value and references. 

<img alt="In action" src="https://s3.amazonaws.com/stonemason/cdn/dist/awscfncli/changeset-execute-demo-01.gif">

## Usage
    
    cfn COMMAND SUBCOMMAND STACK_CONFIG [ARGS]...

To view a list of available subcommands, type:

    cfn COMMAND --help

To view help of a particular subcommand, type:
    
    cfn COMMAND SUBCOMMAND --help


Supported commands:

  - `template`
    - `validate` - Validate template specified in the config
  - `stack`
    - `deploy` - Deploy a new stack  
    - `update` - Update stack
    - `describe` - Describe stack status
    - `tail` - Print stack events
    - `delete` - Delete the stack
  - `changeset`
    - `create` - Create a new changeset
    - `list` - List ChangeSet of stack
    - `describe` - Describe changes
    - `execute` - Update stack using ShangeSet

`STACK_CONFIG` is a simple `YAML` file describes stack deploy parameters:

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

Install using [pip](https://pip.pypa.io/), from [pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli

## Tutorial

[Read the tutorial](https://kotaimen.github.io/awscfncli/)

## AWS Credentials

Check [`boto3` document](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration).
