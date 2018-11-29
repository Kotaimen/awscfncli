# -*- coding: utf-8 -*-

import botocore.exceptions


class Boto3OutputStore(object):
    def __init__(self, contexts, pretty_printer):
        self._contexts = contexts
        self._outputs = dict()
        self._ppt = pretty_printer

    def collect_stack_outputs(self, *attributes):
        for attribute in attributes:
            try:
                qualified_name, attribute_name = attribute.rsplit('.', 1)
            except Exception as e:
                self._ppt.secho(
                    'Invalid Config Reference %s' % attribute,
                    color='yellow')
                raise e

            for context in self._contexts:
                if context.stack_key != qualified_name:
                    continue

                try:
                    cfn = context.session.resource('cloudformation')

                    stack_name = context.parameters['StackName']
                    stack = cfn.Stack(stack_name)

                    stack.load()
                    status = stack.stack_status
                    if status not in (
                            'CREATE_COMPLETE',
                            'ROLLBACK_COMPLETE',
                            'UPDATE_COMPLETE',
                            'UPDATE_ROLLBACK_COMPLETE'):
                        continue
                except Exception as e:
                    self._ppt.secho(
                        'Collect Outputs: Unable to access outputs from %s' % qualified_name,
                        color='yellow')
                    raise e

                if stack.outputs:
                    outputs = dict(
                        map(lambda o: (
                            '.'.join((context.stack_key, o['OutputKey'])),
                            o['OutputValue']),
                            stack.outputs))
                    if attribute not in outputs:
                        raise RuntimeError('Collect Outputs: Attribute %s not found' % attribute)

                    self._ppt.secho(
                        'Collected outputs from %s' % qualified_name, color='yellow')
                    self._outputs.update(outputs)

    def get_outputs(self):
        return self._outputs
