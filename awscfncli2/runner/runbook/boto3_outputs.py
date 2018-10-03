# -*- coding: utf-8 -*-

import botocore.exceptions


class Boto3OutputStore(object):
    def __init__(self, contexts, pretty_printer):
        self._contexts = contexts
        self._outputs = dict()
        self._ppt = pretty_printer

    def collect_stack_outputs(self):
        for context in self._contexts:
            cfn = context.session.resource('cloudformation')

            stack_name = context.parameters['StackName']
            stack = cfn.Stack(stack_name)

            try:
                stack.load()
                status = stack.stack_status
                if status not in (
                        'CREATE_COMPLETE',
                        'ROLLBACK_COMPLETE',
                        'UPDATE_COMPLETE',
                        'UPDATE_ROLLBACK_COMPLETE'):
                    self._ppt.secho(
                        'Collect Ouputs: Stack %s is not in COMPLETE status, skip' % stack_name,
                        color='yellow')
                    continue
            except botocore.exceptions.ClientError:
                self._ppt.secho(
                    'Collect Ouputs: Stack %s is missing, skip' % stack_name,
                    color='yellow')
                continue

            if stack.outputs:
                outputs = dict(
                    map(lambda o: (
                        '.'.join((context.stack_key, o['OutputKey'])),
                        o['OutputValue']),
                        stack.outputs))
                self._outputs.update(outputs)

    def get_outputs(self):
        return self._outputs
