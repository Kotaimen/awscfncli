# -*- coding: utf-8 -*-

import sys

from .boto3_context import Boto3DeploymentContext
from .boto3_outputs import Boto3OutputStore
from .base import RunBook


class Boto3RunBook(RunBook):
    def __init__(self, profile, artifact_store, manager, selector, pretty_printer):
        RunBook.__init__(self)

        self._profile = profile
        self._artifact_store = artifact_store
        self._manager = manager
        self._selector = selector
        self._ppt = pretty_printer

        selected_deployments = self._manager.query_stacks(
            self._selector.stage_pattern,
            self._selector.stack_pattern)
        selected_stack_keys = list(
            d.stack_key.qualified_name for d in selected_deployments)

        if len(selected_deployments) == 0:
            self._ppt.secho('No stack matches specified pattern.', fg='red')
            self._ppt.secho('Available stacks are:')
            for s in self._manager.query_stacks():
                self._ppt.secho(' {}'.format(s.stack_key.qualified_name))
            sys.exit()

        whole_deployments = self._manager.query_stacks()
        whole_contexts = []
        for deployment in whole_deployments:
            context = Boto3DeploymentContext(
                self._profile, self._artifact_store, deployment, self._ppt)
            if deployment.stack_key.qualified_name in selected_stack_keys:
                self._contexts.append(context)
            whole_contexts.append(context)

        self._output_store = Boto3OutputStore(whole_contexts, self._ppt)

    def pre_run(self, command, context):
        if not command.SKIP_UPDATE_REFERENCES:
            attributes = context.get_parameters_reference()
            self._output_store.collect_stack_outputs(*attributes)
            context.update_parameters_reference(**self._output_store.get_outputs())
        context.make_boto3_parameters()
