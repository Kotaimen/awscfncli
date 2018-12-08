from collections import namedtuple

import botocore.exceptions

from .command import Command
from .utils import is_stack_does_not_exist_exception

class StackStatusOptions(namedtuple('StackStatusOptions',
                                    ['dry_run', 'stack_resources',
                                     'stack_exports'])):
    pass


dummy_stack = namedtuple('dummy_stack', ['stack_name', 'stack_status'])


class StackStatusCommand(Command):
    SKIP_UPDATE_REFERENCES = True

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        self.ppt.pprint_stack_name(stack_context.stack_key,
                                   parameters['StackName'])
        # shortcut since dry run is already handled in cli package
        if self.options.dry_run:
            return

        # metadata and parameters only get printed when verbosity>0
        self.ppt.pprint_metadata(metadata)
        self.ppt.pprint_parameters(parameters)

        cfn = session.resource('cloudformation')
        stack = cfn.Stack(parameters['StackName'])

        try:
            stack.stack_status
        except botocore.exceptions.ClientError as ex:
            if is_stack_does_not_exist_exception(ex):
                # make a "dummy" stack object so prettyprint is happy
                stack = dummy_stack(parameters['StackName'], 'STACK_NOT_FOUND')
                self.ppt.pprint_stack(stack, status=True)
                return
            else:
                raise

        self.ppt.pprint_stack(stack, status=True)

        if self.options.stack_resources:
            self.ppt.pprint_stack_resources(stack)

        if self.options.stack_exports:
            self.ppt.pprint_stack_parameters(stack)
            self.ppt.pprint_stack_exports(stack, session)
            client = session.client('cloudformation')

