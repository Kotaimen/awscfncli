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

To view a list of available subcommands, type:

    cfn-cli COMMAND --help

To view help of a particular subcommand, type:
    
    cfn-cli COMMAND SUBCOMMAND --help   


Options:

- `-f, --file`: Specify an alternate configuration file, (default:
  `cfn-cli.yml`)
- `-t, --stage`: Specify a deployment stage, (default: `Default`)
- `-s, --stack`: Specify a stack name, (default: `*`)
- `--profile`: Override AWS profile specified in the configuration 
- `--region`: Override AWS region specified in the configuration 
- `-1, --one`: Select only the first matching stack if glob is used in 
   stage/stack options
- `--verbose`: Be more verbose

By default, `cfn-cli` will try to locate `cfn-cli.yml` file in current 
directory, override this using `-f` option.

Stages and stacks can be selected using globs:
    
    cfn-cli --stack=DDB* stack deploy

Options can be specified using environment variables:

    CFNCLI_STACK=DDB cfn-cli stack deploy 

Supported commands/subcommands:

 -  `stack`
    - `deploy` - Deploy new stack  
    - `update` - Update stack
    - `describe` - Describe stack status
    - `tail` - Print stack events
    - `delete` - Delete stack
 - `changeset`
    - `sync` - Create a ChangeSet and execute it

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