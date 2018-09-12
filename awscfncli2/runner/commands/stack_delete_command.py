from collections import namedtuple

import botocore.exceptions

from ...cli.utils import StackPrettyPrinter
from .utils import update_termination_protection, \
    is_stack_does_not_exist_exception


class StackDeleteOptions(namedtuple('StackDeployOptions',
                                    ['no_wait',
                                     'ignore_missing'])):
    pass


class StackDeleteCommand(object):

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        assert isinstance(options, StackDeleteOptions)
        self.ppt = pretty_printer
        self.options = options

    def run(self, session, parameters, metadata):
        self.ppt.pprint_stack_name(metadata['StackKey'],
                                   parameters['StackName'],
                                   'Deleting stack ')

        cfn = session.resource('cloudformation')

        self.ppt.pprint_session(session)
        self.ppt.pprint_parameters(parameters)

        # call boto3
        stack = cfn.Stack(parameters['StackName'])
        try:
            update_termination_protection(session, parameters, self.ppt)
            self.ppt.pprint_stack(stack)
            stack.delete()
        except botocore.exceptions.ClientError as ex:
            if self.options.ignore_missing and \
                    is_stack_does_not_exist_exception(ex):
                self.ppt.secho(str(ex), fg='red')
                return
            else:
                raise

        # wait until delete complete
        if self.options.no_wait:
            self.ppt.secho('Stack is being deleted.')
        else:
            self.ppt.wait_until_delete_complete(session, stack)
            self.ppt.secho('Stack delete complete.', fg='green')
