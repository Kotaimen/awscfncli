from collections import namedtuple

from ...config import CANNED_STACK_POLICIES
from .command import Command
from .utils import update_termination_protection, \
    is_no_updates_being_performed_exception


class StackUpdateOptions(namedtuple('StackUpdateOptions',
                                    ['no_wait',
                                     'use_previous_template',
                                     'ignore_no_update',
                                     'override_policy'])):
    pass


class StackUpdateCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print stack qualified name
        self.ppt.pprint_stack_name(
            stack_context.stack_key,
            parameters['StackName'],
            'Updating stack '
        )

        # create boto3 cfn resource
        cfn = session.resource('cloudformation')
        self.ppt.pprint_session(session)

        # manipulate stack parameters for update call
        if self.options.use_previous_template:
            parameters.pop('TemplateBody', None)
            parameters.pop('TemplateURL', None)
            parameters['UsePreviousTemplate'] = True
        else:
            # packaging if necessary
            stack_context.run_packaging()

        parameters.pop('DisableRollback', None)
        parameters.pop('OnFailure', None)
        termination_protection = parameters.pop('EnableTerminationProtection',
                                                None)

        if self.options.override_policy is not None:
            self.ppt.secho(
                'Overriding stack policy with {} during update'.format(
                    self.options.override_policy), fg='red')
            parameters['StackPolicyDuringUpdateBody'] = \
                CANNED_STACK_POLICIES[self.options.override_policy]

        self.ppt.pprint_parameters(parameters)

        # termination protection state should be updated no matter
        # stack's update succeeded or not
        update_termination_protection(session,
                                      termination_protection,
                                      parameters['StackName'],
                                      self.ppt)

        # calling boto3...
        stack = cfn.Stack(parameters['StackName'])
        try:
            stack.update(**parameters)
        except Exception as ex:
            if self.options.ignore_no_update and \
                    is_no_updates_being_performed_exception(ex):
                self.ppt.secho(str(ex), fg='red')
                return
            else:
                raise

        self.ppt.pprint_stack(stack)

        # wait until update is complete
        if self.options.no_wait:
            self.ppt.secho('Stack update started.')
        else:
            self.ppt.wait_until_update_complete(session, stack)
            self.ppt.secho('Stack update complete.', fg='green')

