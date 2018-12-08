# AWS CloudFormation CLI

Friendly AWS CloudFormation CLI.

## Introduction

`awscfncli` helps build and manage complex AWS CloudFormation stacks. 

Features:

- Manage stacks in different accounts & regions in a single YAML config file.
- Organize stack using stages and operate on subset using unix globs.
- Cross-stack parameter reference across account & region.
- Automatically package and upload template resources.
- Push button SAM support using `stack sync` command.
- Display and tracking stack events in the console.
 
## Install

Install using [pip](https://pip.pypa.io/) from 
[pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli2

To enable click supported auto-complete, add following line to `.bachrc`
    
    eval "$(_CFN_CLI_COMPLETE=source cfn-cli)"

## Usage

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...]

To view a list of available subcommands, use:

    cfn-cli COMMAND --help

Options:

- `-f, --file`: Specify an alternate config file, (default:
    `cfn-cli.yml`).
- `-s, --stack`: Specify stacks to operate on, defined by
    `STAGE_NAME.STACK_NAME`, default value is `*`, which means
    all stacks in all stages.
- `--profile`: Override AWS profile specified in the config.
- `--region`: Override AWS region specified in the config.
- `--artifact-store`: Override ArtifactStore (AWS bucket name) specified in the config.
- `--verbose`: Be more verbose.

Options can also be specified using environment variables:

    CFN_STACK=Default.Table1 cfn-cli stack deploy

By default, `cfn-cli` will try to locate `cfn-cli.yml` or `cfn-cli.yaml` file 
in current directory, override this behaviour using `-f` option.

### Stack Selector

Individual stack can be selected using full qualified name:

    cfn-cli -s Default.Table2 status

Unix globs is supported when selecting stacks:

    cfn-cli -s Default.Table* status
    cfn-cli -s Def*.Table1 status

If `.` is missing from stack selector, `cfn-cli` will assume
stage name `*` is specfied, thus `*` is equivalent to 
`*.*`, which means all stacks in all stages.

### Available Commands

Use `--help` to see help on a particular command.

- `validate` - Validate template.
- `status` - List status of selected stacks.
- `generate` - Generate a config.
- `stack`
    - `sync` - Create ChangeSet and execute it (required by SAM).
    - `deploy` - Deploy new stacks.
    - `update` - Update stacks.
    - `describe` - Describe stacks details (same as `status`)
    - `tail` - Print stack events.
    - `delete` - Delete stacks.
    - `cancel` - Cancel stack update.

## Automatic Packaging

If a template contains property which requires a S3 url or text block,
Set `Package` parameter to `True` so the resource will be automatically 
upload to a S3 bucket, and S3 object location is inserted into the 
resource location.

This feature is particular useful when your property is a lambda source 
code, SQL statements or some kind of configuration.

By default, the artifact bucket is `awscfncli-${AWS_ACCOUNT_ID}-${AWS_RERION}`,
and the bucket will be created automatically.

You can override the default bucket using `ArtifactStore` parameter

The following resource property are supported by `awscfncli` and official
`aws cloudformation package` command:

- `BodyS3Location` property for the `AWS::ApiGateway::RestApi` resource
- `Code` property for the `AWS::Lambda::Function` resource
- `CodeUri` property for the `AWS::Serverless::Function` resource
- `ContentUri` property for the `AWS::Serverless::LayerVersion` resource
- `DefinitionS3Location` property for the `AWS::AppSync::GraphQLSchema` resource
- `RequestMappingTemplateS3Location` property for the `AWS::AppSync::Resolver` resource
- `ResponseMappingTemplateS3Location` property for the `AWS::AppSync::Resolver` resource
- `DefinitionUri` property for the `AWS::Serverless::Api` resource
- `Location` parameter for the `AWS::Include` transform
- `SourceBundle` property for the `AWS::ElasticBeanstalk::ApplicationVersion` resource
- `TemplateURL` property for the `AWS::CloudFormation::Stack` resource

The following resource property are supported by `awscfncli`:

- `ApplicationCode` property for the `AWS::KinesisAnalytics::Application`
  resource
- `DefinitionString` property for the `AWS::StepFunctions::StateMachine`
  resource
  
## Config File

### Anatomy
TODO

### Blueprints and Inheritance 
TODO

### Stages and Ordering
TODO

### Cross Stack Reference
TODO

## Migrate from 2.0.x

### Config File

If you are using new "cross stack reference" feature then version `3` is required:

```yaml
Version: 3
```
Also `NotificationARNs`, `ResourceTypes`, `RollbackConfiguration` are supported now but no changes is required if old config file is not using them.

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
