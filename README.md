# AWS CloudFormation CLI

AWS CloudFormation stack manager.

## Introduction

`awscfncli` is a tool that helps build and manage complex AWS 
CloudFormation stacks.

Features:

- Single YAML configuration file for:
    - Deployment configuration.
    - Stack parameters.
- Manage stacks in different regions and accounts.
    - Group collection of stacks as stages.
    - Operate on a set of stacks using globs (eg: `dev.db*`).
    - Stack blueprint and YAML tags to ease configuration file writing.
- Automatic packaging template resources:
    - Lambda function packages
    - Nested stacks
    - SQL statements
- Automatic applies template transform (SAM support).
- Automatic ChangeSet synchronization.
- Display and tracking stack events in the console.
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
- `--artifact-store`: Override ArtifactStore (AWS bucket name) specified in the config.
- `-1, --one`: Select only the first matching stack if glob 
    is used in `--stack` option.
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

> Be careful when executing `stack delete` command, as default 
> behaviour is delete all stacks.

### Available Commands

- `validate` - Validate template.
- `status` - List status of selected stacks.
- `stack`
    - `sync` - Create ChangeSet and execute it (required by SAM).
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

`awscfncli` config is a YAML formatted text file with `.yaml` and `.yml`
extension. `awscfncli` uses these files as instructions to manage and deploy 
AWS CloudFormation templates. In a `awscfncli` config, you can describe how you
are going to deploy your stack with parameters such as account profile, region,
stack name, capabilities, teminal protections and etc. With `awscfncli` you can
record the exact parameters used to deploy a stack and keep them under version
control. You can also group your stacks into different stages in a more
enterprise way such as DEV, QA and PROD. Every stack will be contained in one
stage. You can specify your own stage name.

For example, if you deploy a template with the following config file. `awscfncli`
will deploy a stack named Test in region us-east-1 with your default
aws credential. The stack will be in a stage called *`Default`* and identified
by *`Stack1`*.


```yaml
Version: 2
Stages:
  Default:
    Stack1:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
      Region:            us-east-1
      StackName:         Test
      Capabilities:      [CAPABILITY_IAM]
```

You can also specify multiple stacks in different stage and configure these stacks
with separate parameters. For example, in the following config file,
two stacks are deployed with different parameters in different stages.
The stacks in *"Dev"* stage are deployed using dev profile with
small read/write capacities and the stacks in *"Prod"* are deployed using
prod profile with large read/write capacities.


```yaml
Version: 2
Stages:
  Dev:
    Stack1:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
      Region:            us-east-1
      Profile:           dev
      StackName:         DevDDB
      Parameters:
        ReadCapacityUnits:      5
        WriteCapacityUnits:     5
        HashKeyElementName:     id
    Stack2:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
      Region:            us-east-2
      Profile:           dev
      StackName:         DevDDB
      Parameters:
        ReadCapacityUnits:      5
        WriteCapacityUnits:     5
        HashKeyElementName:     id
  Prod:
    Stack1:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
      Region:            us-east-1
      Profile:           prod
      StackName:         DDB
      Parameters:
        ReadCapacityUnits:      100
        WriteCapacityUnits:     100
        HashKeyElementName:     id
    Stack2:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
      Region:            us-east-2
      Profile:           prod
      StackName:         DDB
      Parameters:
        ReadCapacityUnits:      100
        WriteCapacityUnits:     100
        HashKeyElementName:     id
```

In many cases, you may want to deploy stacks with a few parameters changes only. So to
reuse stack configs and save your time of typing, you can use *config inheritance*.
You can predefine a named template of stack config in the *Blueprints* section
and extends it in your stages. Take the above config file as an example, by using Blueprints it
could be rewritten in the following way:

```yaml

Version: 2
Blueprints:
  BaseDDB:
    Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
    Parameters:
      ReadCapacityUnits:      5
      WriteCapacityUnits:     5
      HashKeyElementName:     id
Stages:
  Dev:
    Stack1:
      Extends:           BaseDDB
      Region:            us-east-1
      Profile:           dev
      StackName:         DevDDB
    Stack2:
      Extends:           BaseDDB
      Region:            us-east-2
      Profile:           dev
      StackName:         DevDDB
  Prod:
    Stack1:
      Extends:           BaseDDB
      Region:            us-east-1
      Profile:           prod
      StackName:         DDB
      Parameters:
        ReadCapacityUnits:      100
        WriteCapacityUnits:     100
    Stack2:
      Extends:           BaseDDB
      Region:            us-east-2
      Profile:           prod
      StackName:         DDB
      Parameters:
        ReadCapacityUnits:      100
        WriteCapacityUnits:     100
```

You can also extend your stack configuration by using multiple blueprints, like this:

```yaml
  Version: 2
  Blueprints:
    BaseDDB:
      Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/DynamoDB_Table.template
      Parameters:
        ReadCapacityUnits:      5
        WriteCapacityUnits:     5
        HashKeyElementName:     id
    ProdOverrides:
      Parameters:
        ReadCapacityUnits:      100
        WriteCapacityUnits:     100
      
  ...

  Prod:
    Stack1:
      Extends:           [ BaseDDB, ProdOverrides ]
      Region:            us-east-1
      Profile:           prod
      StackName:         DDB
  
  ... 
  ```

For details about rules of how parameters are extended, please see the
following chapter `Config Inheritance`.

### Deployment Order

By default, stages and stacks are deployed by the order they are 
specified in the configuration file.
If this is not expected behavior, overwrite this using `Order`, you can 
change both stack deployment order and stage deployment order:

```yaml
Stages:
  Foundation:
    Order: 0
    VPC:
      Order: 0
  Develop:
    Order: 1
    Database:
      Order: 1
    Service:
      Order: 2
  Production:
    Order: 2
    Database:
      Order: 1
    Service:
      Order: 2
```

The above config will deploy these stacks in the stage order first and
then in stack order:

1. Foundation.VPC
2. Develop.Database
3. Develop.Service
4. Production.Database
5. Production.Service

### Config Anatomy

#### Version
The version of the config file. Only support version 1 and 2. This
field is optional. The default version is 2.

#### Blueprints
In this section, you can define named templates of stack config that could
be extended later. You could includes basic parameters
that could be reused in the stack configuration in stages.

#### Stages
Stages are the most important part of cfn-cli configuration. It defines
how and in which environment your templates will be deployed.

You can define multiple stages in the `Stages` section. A stage is a
dict of named stacks. You can reference these stacks with dict key in
the cli command. If you does not specify `StackName` in your stack config.
`awscfncli` will use its dict key as it's stack name.

### Config Inheritance

You can extends or overrides the paramters defined in your blueprints.
Here are the general rules that apply when you extends your config.

Suppose we have base template:
```yaml
Version: 2
Blueprints:
  Base:
    Template:          https://s3.amazonaws.com/cloudformation-templates-us-east-1/IAM_Users_Groups_and_Policies.template
    Region:            us-east-1
    StackName:         Test
    Capabilities:      [CAPABILITY_IAM]
    Tags:
      Project: Demo
      Environment: Dev
    ResourceTypes:
      - AWS::IAM

```

1. Paramters with scale value will be directly replaced. For example, in
the following config, the `Region` will be replace with 'us-west-1'
```yaml
Stages:
  Default:
    Stack1:
      Extends: Base
      Region:  us-west-1
```
2. Paramters with dict value will be updated. Items with same key will be
replaced and new item will be added to the dict. For example, in the
following config, the 'Envrionment' will be replaced with 'Prod' and
the new 'Owner' key will be added to the 'Tags' dict and the 'Project'
remains the same.
```yaml
Stages:
  Default:
    Stack1:
      Extends: Base
      Region:  us-west-1
      Tags:
        Environment: Prod
        Owner: Ray
```
3. Paramters with array value will be append with the new value except
some specific parameter like 'Capabilities'. For example, the following
config will append 'AWS::EC2' to ResourceTypes list.
```yaml
Stages:
  Default:
    Stack1:
      Extends: Base
      Region:  us-west-1
      ResourceTypes:
        - AWS::EC2
```
4. If multiple blueprints are specified in `Extends` clause, they are applied in order of appearance.
5. Special Case List:

    Capabilities: Replace the original value.


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
