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

`awscfncli` uses a yaml config file to manage which stacks to deploy and
how to deploy them. By default, it is cfn-cli.yml.

### Anatomy
The config is composed of the following elements, `Version`, `Stages`
and `Blueprints`.

- `Version` (required): Version of cfn-cli config, support 2 and 3 now.
- `Stages` (required): Definition of the stack to be deployed.
- `Blueprints` (optional): Template of the stack.

The following is a simple example of a typical config:
```yaml
Version: 3

Stages:
  Default:
    DDB:
      Template: DynamoDB_Table.yaml
      Region: us-east-1
      Parameters:
        HashKeyElementName: id
    DDB2ndIdx:
      Template: DynamoDB_Secondary_Indexes.yaml
      Region: us-east-1
      StackPolicy: stack_policy.json
      ResourceTypes:
        - AWS::DynamoDB::Table
      Parameters:
        ReadCapacityUnits: 10

```

A stage could have multiple stacks.
In the above example, Stage `Default` have two stacks `DDB` and `DDB2ndIdx`.
Stack name could be customized and should contain only alpha and numbers.

Each stack may have the following attributes.

- Attributes introduced by `awscfncli`:
    - `Profile`: Profile name of your aws credential
    - `Region`: Eg. us-east-1
    - `Package`: Automatically package your template or not
    - `ArtifactStore`: Name of S3 bucket to store packaged files
    - `Order`: Deployment order of stacks
    - `Extends`: Extend a blueprint
- Attributes introduced by `boto3`:
    - Please refer to [Boto3 Create Stack](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudformation.html#CloudFormation.Client.create_stack)


### Blueprints and Inheritance 
Blueprint serves as a template of a common stack. A stack could extends
a stack and override its attributes with its own attributes.


- Inheritance behaviors:
    - scalar value: replace
    - dict value: update
    - list value: extend


- Special attributes:
    - `Capabilities`: replace

For example, please refer to [Blueprints Example](samples/SAM/api_backend/cfn-cli.yaml)

### Stages and Ordering
Stage and stacks could be deployed according to the order you specified.
Order numbers are positive integers. `cfn-cli` will deploy stacks in
stages with lower order first and in each stage stacks with lower order will
be deployed first

- Stage Order
- Stack Order

```yaml
    Stages:
        Stage1:
            Order: 1
            Stack1:
                Order: 1
            Stack2:
                Order: 2
        Stage2:
            Order: 2

```

For examples, please refer to [Order Example](samples/Nested/StaticWebSiteWithPipeline/cfn-cli.yaml)


### Cross Stack Reference
In config version 3, we support a new feature called cross stack reference.
In many cases, stacks' input depends on outputs from other stacks during deployment,
so this new feature will allow stacks collect their inputs as needed and be deployed
without interruption.

An attribute could reference ouputs of another stack by using
the following syntax:
```
Stack1:
    Parameters:
        VpcId: ${StageName.StackName.OutputName}
```

For example, please refer to [Cross Stack Example](samples/Advanced/VpcPeering/cfn-cli.yml)

*Please Note: You should take care of the order of deployment yourself so
that referenced stack is deployed first*

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
