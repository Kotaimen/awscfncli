import uuid
from collections import namedtuple

from .command import Command
from .utils import is_stack_already_exists_exception, is_stack_does_not_exist_exception


class StackDeployOptions(
    namedtuple('StackDeployOptions',
               [
                   'no_wait',
                   'on_failure',
                   'disable_rollback',
                   'timeout_in_minutes',
                   'ignore_existing',
                   'auto_deploy'
               ])):
    pass


class StackDeployCommand(Command):

    def run(self, stack_context):
        
        if self.options.auto_deploy:
            return self._auto_deploy(stack_context)
        
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
            
    def _auto_deploy(self, stack_context):
        self.ppt.secho('Auto Deploy enabled', fg='yellow')

        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters

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
        stack_name = parameters['StackName']
        stack = cfn.Stack(stack_name)
        stack_status = self._get_stack_status(stack)
        if stack_status is None:
            self._create_stack(cfn, stack_context)
        elif stack_status == 'ROLLBACK_COMPLETE':
            self.ppt.secho('Stack previously failed to create, and must be removed before recreation (status: ROLLBACK_COMPLETE).', fg='yellow')
            self._delete_stack(cfn, stack_context)
            self._create_stack(cfn, stack_context)
        else:
            self._update_stack(cfn, stack_context)

    @staticmethod
    def _get_stack_status(stack):
        try:
            status = stack.meta.client.describe_stacks(StackName=stack.name)
        except Exception as ex:
            if is_stack_does_not_exist_exception(ex):
                return None
            
            raise
        
        return status['Stacks'][0]['StackStatus']

    def _create_stack(self, cfn, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters

        # calling boto3...
        client_request_token = 'awscfncli-deploy-{}'.format(uuid.uuid1())
        stack = cfn.create_stack(ClientRequestToken=client_request_token, **parameters)

        self.ppt.pprint_stack(stack)

        # wait until deployment is complete
        self.ppt.wait_until_deploy_complete(session, stack)
        self.ppt.secho('Stack deployment complete.', fg='green')
            
        return
   
    def _update_stack(self, cfn, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters

        # calling boto3...
        stack = cfn.Stack(parameters['StackName'])
        stack.update(**parameters)

        self.ppt.pprint_stack(stack)

        # wait until deployment is complete
        self.ppt.wait_until_update_complete(session, stack)
        self.ppt.secho('Stack update complete.', fg='green')
            
        return

    def _delete_stack(self, cfn, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters

        # calling boto3...
        stack = cfn.Stack(parameters['StackName'])
        stack.delete()

        self.ppt.pprint_stack(stack)

        self.ppt.wait_until_delete_complete(session, stack)
        self.ppt.secho('Stack delete complete.', fg='green')
            
        return
        