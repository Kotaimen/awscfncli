# AWS CloudFormation CLI
Command Line Interface for AWS CloudFormation.

## Introduction
`cfn-cli` is a simple CLI tool that helps deploy and manage AWS CloudFormation stacks.
If you want a flow and project management tool, try [`cfn-flow`](https://github.com/kickstarter/cfn-flow/blob/master/README.md).

To view a list of commands, type:
    
    cfn --help

To view help of a specific command, type:

    cfn command --help

## Install

TODO (pip?)

## AWS Credentials

Check `boto3` configution document [here](https://boto3.readthedocs.io/en/latest/guide/quickstart.html#configuration).

## Stack Configuration

The stack configuration is a YAML file that specifies the runtime parameters of
a AWS CloudFormation template.

The definition of config scheme is as follows:

```yaml
type: map
mapping:
  "Stack":
    type: map
    mapping:
	  "StackName":
	    type: str
	    required: yes
	  "Region":
	    type: str
	    required: yes
	  "TemplateBody":
	    type: str
	  "TemplateURL":
	    type: str
	  "Parameters":
	    type: map
	  "DisableRollback":
	    type: bool
	  "TimeoutInMinutes":
	    type: int
	  "NotificationARNs":
	    type: seq
	  "Capabilities":
	    type: seq
	  "ResourceTypes":
	    type: seq
	  "RoleARN":
	    type: str
	  "OnFailure":
	    type: str
	  "StackPolicyBody":
	    type: str
	  "StackPolicyURL":
	    type: str
	  "Tags":
	    type: map

```

For more information about parameter values, please refer to 
[Boto3 CloudFormation CreateStack](http://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html#CloudFormation.ServiceResource.create_stack). 

Here is a sample configure that create a `ExampleBucket` Stack using amazon sample
template:
	
```yaml
Stack:
  StackName:              ExampleBucket
  Region:                 ap-northeast-1
  TemplateURL:            "https://s3-ap-northeast-1.amazonaws.com/cloudformation-templates-ap-northeast-1/S3_Website_Bucket_With_Retain_On_Delete.template"

  Tags:
    project:              demo
```
	
