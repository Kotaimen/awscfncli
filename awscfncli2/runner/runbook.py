import threading
from collections import OrderedDict
from .boto3_profile import Boto3Profile
from ..config import ConfigError

import six

CANNED_STACK_POLICIES = {
    'ALLOW_ALL': '{"Statement":[{"Effect":"Allow","Action":"Update:*","Principal":"*","Resource":"*"}]}',
    'ALLOW_MODIFY': '{"Statement":[{"Effect":"Allow","Action":["Update:Modify"],"Principal":"*","Resource":"*"}]}',
    'DENY_DELETE': '{"Statement":[{"Effect":"Allow","NotAction":"Update:Delete","Principal":"*","Resource":"*"}]}',
    'DENY_ALL': '{"Statement":[{"Effect":"Deny","Action":"Update:*","Principal":"*","Resource":"*"}]}',
}


def _normalize_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


def _make_boto3_parameters(parameters, is_packaging):
    # inject parameters
    StackName = parameters['StackName']

    Template = parameters['Template']
    if Template.startswith('https') or Template.startswith('http'):
        # s3 template
        TemplateURL, TemplateBody = Template, None
    elif is_packaging:
        # local template with package=on
        TemplateURL = Template
        TemplateBody = None
    else:
        # local template
        TemplateURL = None
        with open(Template) as fp:
            TemplateBody = fp.read()

    # lookup canned policy
    StackPolicy = parameters['StackPolicy']
    if StackPolicy is not None:
        try:
            StackPolicyBody = CANNED_STACK_POLICIES[StackPolicy]
        except KeyError:
            raise ConfigError(
                'Invalid canned policy "%s", valid values are: %s.' % \
                (StackPolicy, ', '.join(CANNED_STACK_POLICIES.keys())))

    else:
        StackPolicyBody = None

    # Normalize parameter config
    Parameters = parameters['Parameters']
    normalized_params = None
    if Parameters and isinstance(Parameters, dict):
        normalized_params = list(
            {
                'ParameterKey': k,
                'ParameterValue': _normalize_value(v)
            }
            for k, v in
            six.iteritems(OrderedDict(
                sorted(six.iteritems(Parameters)))
            )
        )

    # Normalize tag config
    Tags = parameters['Tags']
    normalized_tags = None
    if Tags and isinstance(Tags, dict):
        normalized_tags = list(
            {'Key': k, 'Value': v}
            for k, v in
            six.iteritems(OrderedDict(
                sorted(six.iteritems(Tags)))
            )
        )

    normalized_config = dict(
        StackName=StackName,
        TemplateURL=TemplateURL,
        TemplateBody=TemplateBody,
        DisableRollback=parameters['DisableRollback'],
        RollbackConfiguration=parameters['RollbackConfiguration'],
        TimeoutInMinutes=parameters['TimeoutInMinutes'],
        NotificationARNs=parameters['NotificationARNs'],
        Capabilities=parameters['Capabilities'],
        ResourceTypes=parameters['ResourceTypes'],
        RoleARN=parameters['RoleARN'],
        OnFailure=parameters['OnFailure'],
        StackPolicyBody=StackPolicyBody,
        Parameters=normalized_params,
        Tags=normalized_tags,
        ClientRequestToken=parameters['ClientRequestToken'],
        EnableTerminationProtection=parameters[
            'EnableTerminationProtection'],
    )

    # drop all None and empty list
    return dict(
        (k, v) for k, v in six.iteritems(normalized_config) if
        v is not None)


class StackDeploymentContext(object):
    """Deployment context in boto3 ready format"""

    def __init__(self, cli_boto3_profile, stack_deployment):
        self._boto3_profile = Boto3Profile(
            profile_name=stack_deployment.profile['Profile'],
            region_name=stack_deployment.profile['Region']
        )
        self._boto3_profile.update(cli_boto3_profile)
        self._boto3_session = None
        self._session_lock = threading.Lock()

        self._metadata = stack_deployment.metadata.copy()
        self._parameters = _make_boto3_parameters(
            stack_deployment.parameters, self.metadata['Package'])

    @property
    def boto3_profile(self):
        return self._boto3_profile

    @property
    def boto3_session(self):
        with self._session_lock:
            if self._boto3_session is None:
                self._boto3_session = self.boto3_profile.get_boto3_session()
        return self._boto3_session

    @property
    def metadata(self):
        return self._metadata

    @property
    def parameters(self):
        return self._parameters


class RunBook(object):
    """Run command on selected stacks"""

    def __init__(self, cli_boto3_profile, stack_deployments):
        assert isinstance(cli_boto3_profile, Boto3Profile)

        self.contexts = list(
            StackDeploymentContext(cli_boto3_profile, d)
            for d in stack_deployments
        )

    def run(self, command):
        for context in self.contexts:
            command.run(
                session=context.boto3_session,
                parameters=context.parameters,
                metadata=context.metadata
            )
