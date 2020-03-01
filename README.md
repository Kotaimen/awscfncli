# AWS CloudFormation CLI

The missing CloudFormation CLI.

> [Official](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/what-is-cloudformation-cli.html)  `cfncli` is not designed to manage stacks at this point. 

[TOC]

## Introduction

`awscfncli` helps build and manage AWS CloudFormation stacks. 

Highlights:

- Manage stacks in different accounts and regions use single YAML config file.
- Cross-stack parameter reference works cross-region and cross-account.
- Organize stack using stages and blueprints.
- Automatically package and upload template resources.
- Push button SAM deployment using `stack sync` command.
- Display and track stack events in the CLI.
- List stack resources, outputs and exports in the CLI.

## Install

Install from [pypi](https://pypi.python.org/pypi/awscfncli):

    pip install --user --pre awscfncli2 

When install globally, use [`pipx`](https://github.com/pipxproject/pipx) is recommended:

    pipx install awscfncli2 

## Usage

### Quickstart

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...]

To view a list of available subcommands, use:

    cfn-cli COMMAND --help

Options:

- `-f, --file`: Specify an alternate config file.
- `-s, --stack`: Specify stacks to operate on, defined by `STAGE_NAME.STACK_NAME`, default value is `*`, which means 
  all stacks in all stages.
- `--profile`: Override AWS profile specified in the config or environment variable `AWS_PROFILE`.
- `--region`: Override AWS region specified in the config.
- `--artifact-store`: Override bucket used for template transform/packaging specified in the config.
- `--verbose`: Be more verbose.

Options can also be specified using environment variables:

    CFN_STACK=Default.Table1 cfn-cli stack deploy

By default, `cfn-cli` tries to locate `cfn-cli.yml` or `cfn-cli.yaml` file in current directory, override this use `-f`.

### Stack Selector

Individual stack can be selected using full qualified name:

    cfn-cli -s Default.Table2 status

Or, select stacks use Unix globs:

    cfn-cli -s Default.Table* status
    cfn-cli -s Def*.Table1 status

If `.` is missing from stack selector, `cfn-cli` will assume stage name `*` is specified.

### Commands

Use `--help` to see help on a particular command.

- `generate` - Generate sample configuration file.
- `status` - Print stack status and resources.
- `validate` - Validate template file.
- `stack` - Stack operations.
    - `sync` -Apply changes using ChangeSets
    - `deploy` - Deploy new stacks.
    - `update` - Update existing stacks.
    - `tail` - Print stack events.
    - `delete` - Delete stacks.
    - `cancel` - Cancel stack update.
- `drift` - Drift detection.
    - `detect` - Detect stack drifts.
    - `diff` - Show stack resource drifts.

### Auto Completion

Auto completion is supported by [`click_completion`](https://github.com/click-contrib/click-completion/tree/master/click_completion), 
supported shells are:
 `bash`, `zsh` , `fish` and `Powershell`.  

To install auto completion, run this in target shell:

```
> cfn-cli --install-completion
fish completion installed in /Users/Bob/.config/fish/completions/cfn-cli.fish
```

Supported completion:

- Commands and sub commands:
  ```
  > cfn-cli drift d<TAB><TAB> 
  detect  (Detect stack drifts.)  diff  (Show stack resource drifts.)
  ```
- Options and parameters:
  ```
  > cfn-cli stack deploy --<TAB> <TAB>
  --disable-rollback  (Disable rollback if stack creation failed. You can specify ei…)
  --help                                                 (Show this message and exit.)
  --ignore-existing               (Don't exit with error if the stack already exists.)
  --no-wait                                (Exit immediately after deploy is started.)
  --on-failure  (Determines what action will be taken if stack creation fails. This …)
  --timeout-in-minutes  (The amount of time in minutes that can pass before the stac…)
  ```
- Parameter choices:
  ```
  > cfn-cli stack deploy --on-failure <TAB> <TAB>
    DELETE  DO_NOTHING  ROLLBACK  
  ```

- Dynamic complete for `--profile`  by search profile name in `awscli` config:
  ```
  > cfn-cli -p <TAB><TAB>
  default
  prod
  staging
  ```
- Dynamic complete for `--stack`  by search stack name in `cfn-cli` config:
  ```
  > cfn-cli -s <TAB><TAB>
  Develop.ApiBackend-Develop           (ApiBackend-Develop)
  Production.ApiBackend-Production  (ApiBackend-Production)
  Staging.ApiBackend-Staging           (ApiBackend-Staging)
  ```

### Automatic Packaging

If a template contains property which requires a S3 url or text block, Set stack `Package` parameter to `True` tells 
`cfn-cli` to package the resource automatically and upload to a S3 artifact bucket, and S3 object location is inserted 
into the resource location.

This feature is particular useful when your property is a lambda source code, SQL statements or some kind of 
configuration.

By default, the artifact bucket is `awscfncli-${AWS_ACCOUNT_ID}-${AWS_RERION}`, and it will be created automatically 
on first run.  Override the default bucket using `ArtifactStore` parameter.

The following resource property are supported by `awscfncli` and official `aws cloudformation package` command:

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
- `Command.ScriptLocation` property for the `AWS::Glue::Job` resource

> To package a template build by `awssamcli`, point `Template` parameter to `sam build` output.

## Configuration

`awscfncli` uses a `YAML` config file to manage which stacks to deploy and how to deploy them. By default, 
it is `cfn-cli.yml`.

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
stages with lower order first and in each stage stacks with lower order will be deployed first.

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

In many cases, a stack's input parameter depends on output from other stacks during deployment.  Cross stack reference allows stacks collect their inputs from outputs form other stacks, including stacks deployed to other region and account.

An stack parameter can reference ouputs of another stack in same configuration file by using the following syntax:

```yaml
Stack1:
    Parameters:
        VpcId: ${StageName.StackName.OutputName}
```

This feature make managing related cross-account and/or cross-region stacks much easier.
See [VPC peering](samples/Advanced/VpcPeering/cfn-cli.yml) and [CodePipeline](https://github.com/Kotaimen/sample-python-sam-ci/blob/master/cfn-cli.sample400.yaml) for example.

> Note: Take care of the order of deployment so eferenced stack is deployed first.

## Breaking Changes in 3.0

Generally only major version changes cli and config syntax, and support of last config version is gaunteered.

### CLI

- `stack describe` is depecated, use `status` instead.
- `sync` now defaults to `--confirm`, use `--no-confirm` to overwrite this.

## Breaking Changes in 2.1

### CLI

- `cfn` is renamed to `cfn-cli` to avoid conflict with `troposphere`. 
- `template` command is removed.
- `changeset` command is removed, replaced by `sync` command.
- Because config file supports multiple stages and stacks, stack selector must be specified when you want to operate a subset of stacks.

### Config

"Cross stack reference" feature requires version `3`:

```yaml
Version: 3
Stages:
  Default:
    ...
```

Parameter `NotificationARNs`, `ResourceTypes`, `RollbackConfiguration` are supported now but no changes is required if old config file is not using them.

## Breaking Changes in 2.0

New configuration file supports multiple stages and stacks, to convert an `0.x` configure file to current version, do following:

1. Add following block to the head of conf file and indent the rest properly:

```yaml
Version: 3
Stages:
  Default:
    << old config file >>
```

2. Change any `TemplateURL` or `TemplateBody` parameter to `Template`:

  Old:

  ```yaml
  Stack:
    TemplateURL:          https://s3.amazonaws.com/...
    Region:               us-east-1
    StackName:            SampleIAMUsersGroupsAndPolicies
    Capabilities:         [CAPABILITY_IAM]
  ```

  New:

  ```yaml
  Version: 2
  Stages:
    Default:
      Stack:
        Template:          https://s3.amazonaws.com/...
        Region:               us-east-1
        StackName:            SampleIAMUsersGroupsAndPolicies
        Capabilities:         [CAPABILITY_IAM]
  ```

