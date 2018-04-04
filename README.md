# AWS CloudFormation CLI

AWS CloudFormation stack manager.

## Introduction

`awscfncli` is a tool that helps build and manage complex AWS 
CloudFormation stacks.

Features:

- Single YAML configuration file for:
    - Deployment configuration
    - Stack parameters
- Automatic packaging
- Automatic applies Serverless and Include (aka: SAM support)
- Automatic stack ChangeSet synchronization.
- Display and tracking stack events on cli.
- Describe stack status and export values.
 
## Install

Install using [pip](https://pip.pypa.io/) from 
[pypi](https://pypi.python.org/pypi/awscfncli):

    pip install awscfncli

    
## Usage

    cfn-cli [OPTIONS...] COMMAND SUBCOMMAND [ARGS...]

To view a list of available subcommands, use:

    cfn-cli COMMAND --help

Options:

- `-f, --file`: Specify an alternate config file, (default:
    `cfn-cli.yml`)
- `-s, --stack`: Specify stacks to operate on, defined by
    `STAGE_NAME.STACK_NAME`, default value is `*`, which means
    all stacks in `Default` stage.
- `--profile`: Override AWS profile specified in the config.
- `--region`: Override AWS region specified in the config.
- `-1, --one`: Select only the first matching stack if glob 
    is used in `--stack` option.
- `--verbose`: Be more verbose.

Options can also be specified using environment variables:

    CFN_STACK=Default.Table1 cfn-cli stack deploy

By default, `cfn-cli` will try to locate `cfn-cli.yml` file in 
current directory, override this using `-f` option.

Stack can be selected using full qualified name:

    cfn-cli -s Default.Table2 status

`Default` is the stage name and `DDB1` is stack name, unix globs is also 
supported when selecting stacks to operate on:

    cfn-cli -s Default.Table* status
    cfn-cli -s Def*.Table1 status

When `.` is missing from `--stack` option, `cfn-cli` will assume
stage name `Default` is specfied, thus `*` is equivalent to 
`Default.*`.   
 

### Supported Commands

- `sync` - Create a ChangeSet and execute it.
- `status` - List status of selected stacks.
- `stack`
    - `deploy` - Deploy new stacks.
    - `update` - Update stacks.
    - `describe` - Describe stacks details.
    - `tail` - Print stack events.
    - `delete` - Delete stacks.

## Automatic Packaging

If a template contains property which requires a S3 url or text block,
`Package` can be enabled so the resource is be automatically upload to 
a S3 bucket, and S3 object location is inserted into the template.
This is particular useful when your property is a lambda source code, 
sql statements or some kind of configuration.

By default, artifact bucket name is `awscfncli-${AWS_ACCOUNT_ID}-${AWS_RERION}`.
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

## Configuration File

## Migrate from Old Version
