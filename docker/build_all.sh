#!/usr/bin/env bash

set -e

docker build -t awscfncli2-python27 . -f docker/Dockerfile-python27.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-python27  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

docker build -t awscfncli2-python36 . -f docker/Dockerfile-python36.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-python36  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

docker build -t awscfncli2-python37 . -f docker/Dockerfile-python37.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-python37  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

docker build -t awscfncli2-amazonlinux-2017.09 . -f docker/Dockerfile-amazonlinux-2017.09.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-amazonlinux-2017.09  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

docker build -t awscfncli2-amazonlinux-2018.03 . -f docker/Dockerfile-amazonlinux-2018.03.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-amazonlinux-2018.03  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

docker build -t awscfncli2-alpine . -f docker/Dockerfile-alpine.yml
docker run --rm -v ~/.aws:/root/.aws:ro -e AWS_PROFILE=${AWS_PROFILE} awscfncli2-alpine  \
    -v -f /usr/src/app/samples/sample-confg.yml -s Staging.DDBTable1 validate

