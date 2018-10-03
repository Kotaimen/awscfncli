# -*- coding: utf-8 -*-

import os
import json
import string
import threading

from .boto3_params import make_boto3_parameters
from .boto3_profile import Boto3Profile
from .package import package_template
from .base import StackDeploymentContext


def is_local_path(path):
    if os.path.exists(path):
        return True


class ReferenceTemplate(string.Template):
    idpattern = r'(?a:[_a-z][._a-z0-9]*)'


class Boto3DeploymentContext(StackDeploymentContext):
    def __init__(self, profile, deployment, pretty_printer):
        self._boto3_profile = Boto3Profile(
            profile_name=deployment.profile.Profile,
            region_name=deployment.profile.Region
        )
        self._boto3_profile.update(profile)
        self._session = None
        self._session_lock = threading.Lock()

        self._stack_key = deployment.stack_key.qualified_name
        self._metadata = deployment.metadata._asdict()
        self._parameters = make_boto3_parameters(
            deployment.parameters, self.metadata['Package'])

        self._ppt = pretty_printer

    @property
    def stack_key(self):
        return self._stack_key

    @property
    def session(self):
        with self._session_lock:
            if self._session is None:
                self._session = self._boto3_profile.get_boto3_session()
        return self._session

    @property
    def metadata(self):
        return self._metadata

    @property
    def parameters(self):
        return self._parameters

    def update_reference(self, **outputs):
        d = json.dumps(self.parameters)
        c = ReferenceTemplate(d).safe_substitute(**outputs)
        self._parameters = json.loads(c)

    def run_packaging(self):
        """Package templates and resources and upload to artifact bucket"""
        package = self.metadata["Package"]
        artifact_store = self.metadata["ArtifactStore"]

        if package and 'TemplateURL' in self.parameters:
            template_path = self.parameters.get('TemplateURL')
            if is_local_path(template_path):
                packaged_template = package_template(
                    self._ppt,
                    self.session,
                    template_path,
                    bucket_region=self.session.region_name,
                    bucket_name=artifact_store,
                    prefix=self.parameters['StackName'])
                self.parameters['TemplateBody'] = packaged_template
                self.parameters.pop('TemplateURL')
