#!/usr/bin/env bash

set -e

for PYTHON_VERSION in 3.7 3.6 2.7;
do

    docker image build \
        --build-arg PYTHON_VERSION=${PYTHON_VERSION} \
        --tag awscfncli2-python-${PYTHON_VERSION} \
        . -f docker/Dockerfile-python.yml;

    docker run --rm -v ~/.aws:/root/.aws:ro \
        -e AWS_PROFILE=${AWS_PROFILE} \
        awscfncli2-python-${PYTHON_VERSION}  \
        -v \
        -f /usr/src/app/samples/Simple/DynamoDB/cfn-cli.yml \
        validate;

done


for AMAZON_LINUX_VERSION in 2017.09 2018.03;
do

    docker image build \
        --build-arg AMAZON_LINUX_VERSION=${AMAZON_LINUX_VERSION} \
        --tag awscfncli2-amazonlinux-${AMAZON_LINUX_VERSION} \
        . -f docker/Dockerfile-amazonlinux.yml;

    docker run --rm -v ~/.aws:/root/.aws:ro \
        -e AWS_PROFILE=${AWS_PROFILE} \
        awscfncli2-amazonlinux-${AMAZON_LINUX_VERSION}  \
        -v \
        -f /usr/src/app/samples/Simple/DynamoDB/cfn-cli.yml \
        validate;

done

