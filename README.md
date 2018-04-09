# AWS CloudFormation CLI

AWS CloudFormation stack manager.

## Introduction

`awscfncli` is a tool that helps build and manage complex AWS 
CloudFormation stacks.

Features:

- Single YAML configuration file for:
    - Deployment configuration.
    - Stack parameters.
- Automatic packaging template resources.
- Automatic applies Serverless transform (aka: SAM support).
- Automatic stack ChangeSet synchronization.
- Display and tracking stack events on cli.
- Describe stack status and export values.
 
## Install

Install using [pip](https://pip.pypa.io/) from 
[pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli2


## Usage

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...]

To view a list of available subcommands, use:

    cfn-cli COMMAND --help

Options:

- `-f, --file`: Specify an alternate config file, (default:
    `cfn-cli.yml`)
- `-s, --stack`: Specify stacks to operate on, defined by
    `STAGE_NAME.STACK_NAME`, default value is `*`, which means
    all stacks in all stages.
- `--profile`: Override AWS profile specified in the config.
- `--region`: Override AWS region specified in the config.
- `-1, --one`: Select only the first matching stack if glob 
    is used in `--stack` option.
- `--verbose`: Be more verbose.

Options can also be specified using environment variables:

    CFN_STACK=Default.Table1 cfn-cli stack deploy

By default, `cfn-cli` will try to locate `cfn-cli.yml` file in 
current directory, override this using `-f` option.

### Stack Selector

Individual stack can be selected using full qualified name:

    cfn-cli -s Default.Table2 status

Here `Default` is the stage name and `DDB1` is stack name.
Unix globs is supported when selecting stacks:

    cfn-cli -s Default.Table* status
    cfn-cli -s Def*.Table1 status

If `.` is missing from stack selector, `cfn-cli` will assume
stage name `*` is specfied, thus `*` is equivalent to 
`*.*`, which means all stacks in all stages.

> Be careful when executing `stack delete` command, as default 
> behaviour is delete all stacks.

### Supported Commands

- `sync` - Create ChangeSet and execute it.
- `status` - List status of selected stacks.
- `stack`
    - `deploy` - Deploy new stacks.
    - `update` - Update stacks.
    - `describe` - Describe stacks details.
    - `tail` - Print stack events.
    - `delete` - Delete stacks.

## Automatic Packaging

If a template contains property which requires a S3 url or text block,
Set `Package` parameter to `True` so the resource is be automatically 
upload to a S3 bucket, and S3 object location is inserted into the 
resource location.

This feature is particular useful when your property is a lambda source 
code, sql statements or some kind of configuration.

By default, the artifact bucket is `awscfncli-${AWS_ACCOUNT_ID}-${AWS_RERION}`.
and the bucket will be created automatically.

The following resource property are supported by `awscfncli` and official
`aws cloudformation package` command:

- `AWS::ApiGateway::RestApi->BodyS3Location`
- `AWS::Lambda::Function->Code`
- `AWS::Serverless::Function->CodeUri`
- `AWS::Serverless::Api->DefinitionUri`
- `AWS::ElasticBeanstalk::Application-Version->SourceBundle`
- `AWS::CloudFormation::Stack->TemplateURL`

The following resource property are supported by `awscfncli`:

- `AWS::Transform->Location`
- `AWS::KinesisAnalytics::Application->ApplicationCode`
- `AWS::StepFunctions::StateMachine->DefinitionString`

## Config File

> TODO: Write config document and sample here, diff to previous version will be covered blow.  

## Migrate from 0.x

### Config File

New configuration file supports mutilable stages and stacks, to convert an `0.x` configure file to current version,

1. Add following block to the head of conf file and indent properly:

```yaml
Version: 2
Stages:
  Default:
    << old config file >>
```

2. Change any `TemplateURL` or `TemplateBody` parameter to `Template`.

For example:

Old:

```yaml
Stack:
  TemplateURL:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
  Region:               us-east-1
  StackName:            SampleIAMUsersGroupsAndPolicies
  Capabilities:         [CAPABILITY_IAM]
  Parameters:
    Password:           bob180180180
  Tags:
    project:            Bob
```

New:

```yaml
Version: 2
Stages:
  Default:
    Stack:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
      Region:               us-east-1
      StackName:            SampleIAMUsersGroupsAndPolicies
      Capabilities:         [CAPABILITY_IAM]
      Parameters:
        Password:           bob180180180
      Tags:
        project:            Bob
```


### CLI

- `cfn` is renamed to `cfn-cli` to avoid conflict with `troposphere`. 
- `template` command is removed.
- `changeset` command is removed, but a new `sync` command is added.
- Because config file supports mutilable stages and stacks, stack selector must be specified when you want to operate a subset of stacks.


### Sync
New `sync` command combines `aws cloudformation package` and `aws cloudformation deploy` in one step:

	cfn changeset create
	cfn changeset execute

Is replaced by:

	cfn-cli -s sam.api sync

`sync` uses `ChangeSet` interally which is required by the `Serverless` transform (aka: SAM). 

> Note: SAM cannot be used together with nested stacks, this is a 
AWS limit.
	