import os
import threading
from collections import OrderedDict

import six

from .boto3_profile import Boto3Profile
from .package import package_template
from ..config import ConfigError, StackDeployment, CANNED_STACK_POLICIES


def _normalize_value(v):
    if isinstance(v, bool):
        return 'true' if v else 'false'
    elif isinstance(v, int):
        return str(v)
    else:
        return v


def _make_boto3_parameters(parameters, is_packaging):
    # inject parameters
    StackName = parameters.StackName

    Template = parameters.Template
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
    StackPolicy = parameters.StackPolicy
    if StackPolicy is not None:
        try:
            StackPolicyBody = CANNED_STACK_POLICIES[StackPolicy]
        except KeyError:
            # treat as local file
            if os.path.exists(StackPolicy) and os.path.isfile(StackPolicy):
                try:
                    with open(StackPolicy) as fp:
                        StackPolicyBody = fp.read()
                except Exception as ex:
                    raise ConfigError(
                        'Error reading stack policy {}'.format(StackPolicy))
            else:
                raise ConfigError(
                    'Invalid stack policy, either specify a canned policy name '
                    'or a local policy document.')
    else:
        StackPolicyBody = None
    StackPolicyURL = None

    # Normalize parameter config
    Parameters = parameters.Parameters
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
    Tags = parameters.Tags
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
        DisableRollback=parameters.DisableRollback,
        RollbackConfiguration=parameters.RollbackConfiguration,
        TimeoutInMinutes=parameters.TimeoutInMinutes,
        NotificationARNs=parameters.NotificationARNs,
        Capabilities=parameters.Capabilities,
        ResourceTypes=parameters.ResourceTypes,
        RoleARN=parameters.RoleARN,
        OnFailure=parameters.OnFailure,
        StackPolicyBody=StackPolicyBody,
        StackPolicyURL=StackPolicyURL,
        Parameters=normalized_params,
        Tags=normalized_tags,
        ClientRequestToken=parameters.ClientRequestToken,
        EnableTerminationProtection=parameters.EnableTerminationProtection,
    )

    # drop all None and empty list
    return dict(
        (k, v) for k, v in six.iteritems(normalized_config) if
        v is not None)


def is_local_path(path):
    if os.path.exists(path):
        return True


class StackDeploymentContext(object):
    """Stack context in boto3 ready format"""

    def __init__(self, cli_boto3_profile, stack_deployment):
        self._boto3_profile = Boto3Profile(
            profile_name=stack_deployment.profile.Profile,
            region_name=stack_deployment.profile.Region
        )
        self._boto3_profile.update(cli_boto3_profile)
        self._boto3_session = None
        self._session_lock = threading.Lock()

        self._stack_key = stack_deployment.stack_key.qualified_name
        self._metadata = stack_deployment.metadata._asdict()
        self._parameters = _make_boto3_parameters(
            stack_deployment.parameters, self.metadata['Package'])

    @property
    def stack_key(self):
        return self._stack_key

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

    def run_packaging(self, pretty_printer):
        """Package templates and resources and upload to artifact bucket"""
        package = self.metadata["Package"]
        artifact_store = self.metadata["ArtifactStore"]

        if package and 'TemplateURL' in self.parameters:
            template_path = self.parameters.get('TemplateURL')
            if is_local_path(template_path):
                packaged_template = package_template(
                    pretty_printer,
                    self.boto3_session,
                    template_path,
                    bucket_region=self.boto3_session.region_name,
                    bucket_name=artifact_store,
                    prefix=self.parameters['StackName'])
                self.parameters['TemplateBody'] = packaged_template
                self.parameters.pop('TemplateURL')


class RunBook(object):
    """Run command on given deployments"""

    def __init__(self, cli_boto3_profile, stack_deployments):
        assert isinstance(cli_boto3_profile, Boto3Profile)

        # XXX: properly move this to a separated factory
        self._contexts = list()

        for deployment in stack_deployments:
            assert isinstance(deployment, StackDeployment)
            context = StackDeploymentContext(cli_boto3_profile, deployment)
            self._contexts.append(context)

    def run(self, command, rev=False):
        """Runs specified command"""
        if rev:
            stack_contexts = reversed(self.contexts)
        else:
            stack_contexts = self.contexts

        for stack_context in stack_contexts:
            command.run(stack_context)

    @property
    def contexts(self):
        """List of stack contexts to run"""
        return self._contexts
