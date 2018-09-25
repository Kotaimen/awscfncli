# -*- encoding: utf-8 -*-
import os.path

from .config import load_config, ConfigError
from .deployment import StackKey, StackDeployment

CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    'ALLOW_MODIFY': '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    'DENY_DELETE': '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    'DENY_ALL': '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}

with open(os.path.join(os.path.dirname(__file__),
                       'annotated-sample-config.yaml')) as fp:
    ANNOTATED_SAMPLE_CONFIG = fp.read()

with open(os.path.join(os.path.dirname(__file__),
                       'sample-config.yaml')) as fp:
    SAMPLE_CONFIG = fp.read()
