ARG PYTHON_VERSION
FROM python:${PYTHON_VERSION}

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
COPY . /usr/src/app

RUN set -x \
  && pip install .

ENTRYPOINT ["cfn-cli"]
