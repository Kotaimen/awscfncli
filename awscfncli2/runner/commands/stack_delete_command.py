from collections import namedtuple

from .command import Command
from .utils import update_termination_protection, \
    is_stack_does_not_exist_exception


class StackDeleteOptions(namedtuple('StackDeleteOptions',
                                    ['no_wait',
                                     'ignore_missing'])):
    pass


class StackDeleteCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.boto3_session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        self.ppt.pprint_stack_name(stack_context.stack_key,
                                   parameters['StackName'],
                                   'Deleting stack ')

        # create boto3 cfn resource
        cfn = session.resource('cloudformation')
        self.ppt.pprint_session(session)
        self.ppt.pprint_parameters(parameters)

        # packaging if necessary
        stack_context.run_packaging(self.ppt)

        # call boto3
        stack = cfn.Stack(parameters['StackName'])
        try:
            update_termination_protection(
                session,
                parameters.pop('EnableTerminationProtection', None),
                parameters['StackName'],
                self.ppt)
            self.ppt.pprint_stack(stack)
            stack.delete()
        except Exception as ex:
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
