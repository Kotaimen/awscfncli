#!/usr/bin/env bash
set -e

cfn-cli -v -f samples/Simple/DynamoDB/cfn-cli.yml validate

cfn-cli -v -f samples/Simple/DynamoDB/cfn-cli.yml -s Default.DDB stack deploy
cfn-cli -v -f samples/Simple/DynamoDB/cfn-cli.yml -s Default.DDB stack delete -qi

cfn-cli -v -f samples/SAM/api_backend -s Production.ApiBackend-Production stack sync
cfn-cli -v -f samples/SAM/api_backend -s Production.ApiBackend-Production drift detect
cfn-cli -v -f samples/SAM/api_backend -s Production.ApiBackend-Production drift diff
cfn-cli -v -f samples/SAM/api_backend -s Production.ApiBackend-Production stack delete -qi
