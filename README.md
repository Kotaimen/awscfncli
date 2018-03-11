# AWS CloudFormation CLI

Reloading...

Easy AWS CloudFormation stack manager   .

## Introduction

`awscfncli` is a tool that helps you manage AWS CloudFormation stacks.

Features:

- Simple CLI interface.
- YAML stacks configuration file.
- Stack management.
- ChangeSet management.
- Display and tracking stack events, including nested stack.
- Tracking stack export value and references.

 
## Install

Install using [pip](https://pip.pypa.io/), from [pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli
    
## Usage

TBD

## Migrate From Version 0.x

### Entrypoint

To avoid confilct with `troposphere`, cli entrypoint has been renamed 
from `cfn` to `cfn-cli`.

### Config File
To support multi stage environment, config file now contains mutiable 
stack configuration instead of single stack. 
And you don't have to specify config file name if its `cfn-cli.yml`,
(behave like `docker-compose`).

Old syntax:

```
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

New syntax:

```
version: 2
environments:
  Default:
    SampleIAMUsersGroupsAndPolicies:
      Region:               us-east-1
      TemplateURL:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
      Capabilities:         [CAPABILITY_IAM]
      Parameters:
        Password:           bob180180180
      Tags:
        project:            Bob
```

### CLI

You must specify environment and stack name in the CLI. 

Before:
    
    cfn COMMAND SUBCOMMAND STACK_CONFIG [ARGS]...

After:

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...] ENVIRONMENT_NAME STACK_NAME
   