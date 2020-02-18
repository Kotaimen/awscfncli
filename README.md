# AWS CloudFormation CLI

The missing AWS CloudFormation CLI.

> [Official `cfncli`](https://docs.aws.amazon.com/cloudformation-cli/latest/userguide/what-is-cloudformation-cli.html) is not designed to manage stacks at this point. 

## Introduction

`awscfncli` helps build and manage AWS CloudFormation stacks. 

Features:

- Manage stacks in different accounts & regions in a single YAML config file.

- Organize stack using stages and blueprints. 

- Select stacks to operate on using globs.

- Cross-stack parameter reference.

- Automatically package and upload template resources.

- Push button SAM deployment using `stack sync` command.

  > Now `samcli`  is getting better at deploying SAM template automatically.
- Display and tracking stack events in the CLI.

- List stack resources, outputs and exports in the CLI.

## Install

Install using [pip](https://pip.pypa.io/) from [pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli2

If you are install `cfn-cli` globally, using [`pipx`](https://github.com/pipxproject/pipx) is recommended:

    pipx install awscfncli2 

### Auto Completion

Auto completion is supported by `click` and `click_completion`, supported shells are `bash`, `zsh` , `fish` and `Powershell`.  

To install auto completion, run this in target shell:

```
> cfn-cli --install-completion
fish completion installed in /Users/Bob/.config/fish/completions/cfn-cli.fish
```

Three types of auto completions are supported:

- Commands and sub commands.
- Options and parameters.
- Dynamic complete for `--profile` and `--stacks`.

```
> cfn-cli drift d<TAB><TAB> 
detect  (Detect stack drifts.)  diff  (Show stack resource drifts.)

> cfn-cli stack deploy --<TAB> <TAB>
--disable-rollback  (Disable rollback if stack creation failed. You can specify ei…)
--help                                                 (Show this message and exit.)
--ignore-existing               (Don't exit with error if the stack already exists.)
--no-wait                                (Exit immediately after deploy is started.)
--on-failure  (Determines what action will be taken if stack creation fails. This …)
--timeout-in-minutes  (The amount of time in minutes that can pass before the stac…)

> cfn-cli stack deploy --on-failure <TAB> <TAB>
DELETE  DO_NOTHING  ROLLBACK

> cfn-cli -s <TAB><TAB>
Develop.ApiBackend-Develop           (ApiBackend-Develop)
Production.ApiBackend-Production  (ApiBackend-Production)
Staging.ApiBackend-Staging           (ApiBackend-Staging)
```

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
- `Command.ScriptLocation` property for the `AWS::Glue::Job` resource
  
## Configuration

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

New configuration file supports multiple stages and stacks, to convert an `0.x` configure file to current version,

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
- Because config file supports multiple stages and stacks, stack selector must be specified when you want to operate a subset of stacks.


### Sync
New `sync` command combines `aws cloudformation package` and `aws cloudformation deploy` in one step:

    cfn changeset create
    cfn changeset execute

Is replaced by:

    cfn-cli -s sam.api sync

`sync` uses `ChangeSet` internally which is useful when dealing with template transforms (eg: SAM or macros). 

