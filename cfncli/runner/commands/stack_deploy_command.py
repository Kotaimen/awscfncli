import uuid
from collections import namedtuple

from .command import Command
from .utils import is_stack_already_exists_exception


class StackDeployOptions(
    namedtuple('StackDeployOptions',
               [
                   'no_wait',
                   'on_failure',
                   'disable_rollback',
                   'timeout_in_minutes',
                   'ignore_existing'
               ])):
    pass


class StackDeployCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print qualified name
        self.ppt.pprint_stack_name(stack_context.stack_key,
                                   parameters['StackName'],
                                   'Deploying stack ')

        # create boto3 cfn resource
        cfn = session.resource('cloudformation')
        self.ppt.pprint_session(session)

        # packaging if necessary
        stack_context.run_packaging()

        # overwrite using cli parameters
        if self.options.on_failure is not None:
            parameters['OnFailure'] = self.options.on_failure
        if self.options.disable_rollback:
            parameters['DisableRollback'] = self.options.disable_rollback
        if self.options.timeout_in_minutes:
            parameters['TimeoutInMinutes'] = self.options.timeout_in_minutes

        self.ppt.pprint_parameters(parameters)

        # calling boto3...
        try:
            client_request_token = 'awscfncli-deploy-{}'.format(uuid.uuid1())
            stack = cfn.create_stack(
                ClientRequestToken=client_request_token,
                **parameters)
        except Exception as ex:
            # skip existing stack error
            if self.options.ignore_existing and \
                    is_stack_already_exists_exception(ex):
                self.ppt.secho(str(ex), fg='red')
                return
            else:
                raise

        self.ppt.pprint_stack(stack)

        # wait until deployment is complete
        if self.options.no_wait:
            self.ppt.secho('Stack deployment started.')
        else:
            self.ppt.wait_until_deploy_complete(session, stack)
            self.ppt.secho('Stack deployment complete.', fg='green')

