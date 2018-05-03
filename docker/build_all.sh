#!/usr/bin/env bash

docker build -t awscfncli2-python2 . -f docker/Dockerfile-python2.yml
docker run awscfncli2-python3 --version

docker build -t awscfncli2-python3 . -f docker/Dockerfile-python3.yml
docker run awscfncli2-python3 --version

docker build -t awscfncli2-amazonlinux-2017.09 . -f docker/Dockerfile-amazonlinux-2017.09.yml
docker run awscfncli2-amazonlinux-2017.09 --version

docker build -t awscfncli2-alpine . -f docker/Dockerfile-alpine.yml
docker run awscfncli2-alpine --version
