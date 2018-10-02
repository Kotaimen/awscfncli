import os
import threading
import json
import string

from .boto3_params import make_boto3_parameters
from .boto3_profile import Boto3Profile
from .package import package_template
from ..config import StackDeployment


def is_local_path(path):
    if os.path.exists(path):
        return True


class StackReferenceTemplate(string.Template):
    idpattern = r'(?a:[_a-z][._a-z0-9]*)'


class StackDeploymentContext(object):
    """Stack context in boto3 ready format"""

    def __init__(self, cli_boto3_profile, stack_deployment, ouput_store):
        self._boto3_profile = Boto3Profile(
            profile_name=stack_deployment.profile.Profile,
            region_name=stack_deployment.profile.Region
        )
        self._boto3_profile.update(cli_boto3_profile)
        self._boto3_session = None
        self._session_lock = threading.Lock()

        self._stack_key = stack_deployment.stack_key.qualified_name
        self._metadata = stack_deployment.metadata._asdict()
        self._parameters = make_boto3_parameters(
            stack_deployment.parameters, self.metadata['Package'])

        self._output_store = ouput_store

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

    @property
    def outputs(self):
        return self._output_store

    def populate_outputs(self, **outputs):
        for k, v in outputs.items():
            qualified_key = '.'.join((self.stack_key, k))
            if qualified_key in self.outputs:
                raise RuntimeError(
                    'Duplicated Stack Output: %s' % qualified_key)
            else:
                self.outputs[qualified_key] = v

    def update_reference(self):
        d = json.dumps(self.parameters)
        c = StackReferenceTemplate(d).safe_substitute(**self.outputs)
        self._parameters = json.loads(c)

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
        self._outputs = dict()

        for deployment in stack_deployments:
            assert isinstance(deployment, StackDeployment)
            context = StackDeploymentContext(cli_boto3_profile, deployment,
                                             self._outputs)
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
