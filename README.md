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

You can author cfn-cli config file with YAML format.

A cfn-cli config is a description of your AWS CloudFormation Stacks deployed on
AWS. 

From awscfncli 2.0,**Environemnt**is introduced to support managing 
multiple stacks. A config file can now contain multiple 
stack configuration instead of single stack.

Awscfncli now read a config file called `cfn-cli.yml` in the current working 
directory by default. You can override this by specify your config file with 
`-f` option. (behaves like `docker-compose`).


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
Version: 2
Environments:
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

#### Config File Format

##### Format Version (optional)

Currently, two version numbers are supported. Version 1 is for the 
configuration of awscfncli 1.0 and version 2 is for awscfncli 2.0. version
1 will be the default version if you don't specify a version number.

```
Version: VERSION_NUMBER
```

##### Environments (required)

Environment is a concept newly introduced in awscfncli 2.0 that can group
bunches of stacks that serves for a same purpose for you. 

Under section Environments, you could specify multiple environments with 
their name as key. A environment is also a dict of named configuration 
for stacks.

```
Environments:
  Env1:
    Stack1
      Param1: Value1
      Param2: Value2
  Env2:
    Stack2
      Param1: Value1
      Param2: Value2
```

##### Stack (required)

A stack configuration contains parameters required by AWS to create a 
CloudFormation stack. 

Some addtional meta parameters are also required
to construct the connection to AWS, such as your AWS profile name, the
region that you want to deploy your stack and etc. 


```
    Stack1
      Profile: aws profile name
      Region: us-east-1
      
      Param1: Value1
      Param2: Value2
```

For sample configuration, please refer to samples/cfn-cli.yml


### CLI

You must specify environment and stack name in the CLI. 

Before:
    
    cfn COMMAND SUBCOMMAND STACK_CONFIG [ARGS]...

After:

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...] ENVIRONMENT_NAME STACK_NAME
   