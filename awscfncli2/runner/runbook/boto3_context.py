# -*- coding: utf-8 -*-

import os
import threading

from .base import StackDeploymentContext
from .boto3_params import make_boto3_parameters
from .boto3_profile import Boto3Profile
from .package import package_template
from ...config import ConfigError


class Boto3DeploymentContext(StackDeploymentContext):
    def __init__(self, profile, artifact_store, deployment, pretty_printer):
        self._boto3_profile = Boto3Profile(
            profile_name=deployment.profile.Profile,
            region_name=deployment.profile.Region
        )
        self._boto3_profile.update(profile)
        self._session = None
        self._session_lock = threading.Lock()

        self._deployment = deployment

        self._stack_key = deployment.stack_key.qualified_name
        self._metadata = deployment.metadata._asdict()
        self._parameters = deployment.parameters._asdict()

        self._artifact_store = artifact_store
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

    def get_parameters_reference(self):
        return self._deployment.parameters.find_references()

    def update_parameters_reference(self, **outputs):
        self._parameters = self._deployment.parameters.substitute_references(**outputs)

    def make_boto3_parameters(self):
        self._parameters = make_boto3_parameters(
            self._parameters, self.metadata['Package'])

    def run_packaging(self):
        """Package templates and resources and upload to artifact bucket"""
        package = self.metadata["Package"]

        if not package:
            return

        template_path = self.parameters.get('TemplateURL', None)

        if not os.path.exists(template_path):
            raise ConfigError(
                "Can'not find %s. Package is supported for local template only" %
                (template_path))

        artifact_store = self._artifact_store if self._artifact_store else \
            self.metadata["ArtifactStore"]

        template_body, template_url = package_template(
            self._ppt,
            self.session,
            template_path,
            bucket_region=self.session.region_name,
            bucket_name=artifact_store,
            prefix=self.parameters['StackName']
        )

        if template_url is not None:
            # packaged template is too large, use S3 pre-signed url
            self.parameters['TemplateURL'] = template_url
        else:
            # packaged template is passed with request body
            self.parameters['TemplateBody'] = template_body
            self.parameters.pop('TemplateURL')
