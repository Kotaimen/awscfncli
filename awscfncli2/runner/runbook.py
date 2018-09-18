import os
import threading
from collections import OrderedDict
from .boto3_profile import Boto3Profile
from ..cli.utils import package_template
from ..config import ConfigError, StackDeployment, CANNED_STACK_POLICIES

import six


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
            raise ConfigError(
                'Invalid canned policy "%s", valid values are: %s.' % \
                (StackPolicy, ', '.join(CANNED_STACK_POLICIES.keys())))

    else:
        StackPolicyBody = None

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
    """Deployment context in boto3 ready format"""

    def __init__(self, cli_boto3_profile, stack_deployment):
        self._boto3_profile = Boto3Profile(
            profile_name=stack_deployment.profile.Profile,
            region_name=stack_deployment.profile.Region
        )
        self._boto3_profile.update(cli_boto3_profile)
        self._boto3_session = None
        self._session_lock = threading.Lock()

        self._metadata = stack_deployment.metadata._asdict()
        self._metadata['StackKey'] = stack_deployment.stack_key.qualified_name
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

    def run_packaging(self, verbosity=0):
        """Package templates and resources and upload to artifact bucket"""
        package = self.metadata["Package"]
        artifact_store = self.metadata["ArtifactStore"]

        if package and 'TemplateURL' in self.parameters:
            template_path = self.parameters.get('TemplateURL')
            if is_local_path(template_path):
                packaged_template = package_template(
                    self.boto3_session,
                    template_path,
                    bucket_region=self.boto3_session.region_name,
                    bucket_name=artifact_store,
                    prefix=self.parameters['StackName'])
                self.parameters['TemplateBody'] = packaged_template
                self.parameters.pop('TemplateURL')


class RunBook(object):
    """Run command on specified deployments"""

    def __init__(self, cli_boto3_profile, stack_deployments):
        assert isinstance(cli_boto3_profile, Boto3Profile)

        # XXX: properly move this to a separated factory
        self._contexts = list()

        for deployment in stack_deployments:
            assert isinstance(deployment, StackDeployment)
            context = StackDeploymentContext(cli_boto3_profile, deployment)
            context.run_packaging()
            self._contexts.append(context)

    def run(self, command, rev=False):
        """Runs specified command"""
        if rev:
            runs = reversed(self.runs)
        else:
            runs = self.runs

        for context in runs:
            command.run(
                session=context.boto3_session,
                parameters=context.parameters,
                metadata=context.metadata
            )

    @property
    def runs(self):
        """List of stack contexts to run"""
        return self._contexts
