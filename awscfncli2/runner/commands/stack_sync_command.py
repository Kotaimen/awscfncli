import uuid
from collections import namedtuple

import backoff
import botocore.exceptions

from awscfncli2.cli.utils.common import is_not_rate_limited_exception, is_rate_limited_exception
from awscfncli2.cli.utils.pprint import echo_pair
from .command import Command
from .utils import update_termination_protection


class StackSyncOptions(namedtuple('StackSyncOptions',
                                  ['no_wait',
                                   'confirm',
                                   'use_previous_template',
                                   'disable_tail_events'])):
    pass


class StackSyncCommand(Command):

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        # print stack qualified name
        self.ppt.pprint_stack_name(
            stack_context.stack_key,
            parameters['StackName'],
            'Syncing stack '
        )
        self.ppt.pprint_session(session)

        if self.options.use_previous_template:
            parameters.pop('TemplateBody', None)
            parameters.pop('TemplateURL', None)
            parameters['UsePreviousTemplate'] = True
        else:
            stack_context.run_packaging()

        # create cfn client
        client = session.client('cloudformation')

        # generate a unique changeset name
        changeset_name = '%s-%s' % \
                         (parameters['StackName'], str(uuid.uuid1()))

        # get changeset type: CREATE or UPDATE
        changeset_type, is_new_stack = self.check_changeset_type(client,
                                                                 parameters)

        # prepare stack parameters
        parameters['ChangeSetName'] = changeset_name
        parameters['ChangeSetType'] = changeset_type
        parameters.pop('StackPolicyBody', None)
        parameters.pop('StackPolicyURL', None)
        termination_protection = parameters.pop(
            'EnableTerminationProtection', None)

        self.ppt.pprint_parameters(parameters)

        # create changeset
        echo_pair('ChangeSet Name', changeset_name)
        echo_pair('ChangeSet Type', changeset_type)

        result = self.create_change_set(client, parameters)
        changeset_id = result['Id']
        echo_pair('ChangeSet ARN', changeset_id)

        self.ppt.wait_until_changset_complete(client, changeset_id)

        result = self.describe_change_set(client, changeset_name, parameters)
        self.ppt.pprint_changeset(result)

        # termination protection should be set after the creation of stack
        # or changeset
        update_termination_protection(session,
                                      termination_protection,
                                      parameters['StackName'],
                                      self.ppt)

        # check whether changeset is executable
        if result['Status'] not in ('AVAILABLE', 'CREATE_COMPLETE'):
            self.ppt.secho('ChangeSet not executable.', fg='red')
            return

        if self.options.confirm:
            if self.options.no_wait:
                return 
            if not self.ppt.confirm('Do you want to execute ChangeSet?'):
                return

        client_request_token = 'awscfncli-sync-{}'.format(uuid.uuid1())
        self.ppt.secho('Executing ChangeSet...')
        client.execute_change_set(
            ChangeSetName=changeset_name,
            StackName=parameters['StackName'],
            ClientRequestToken=client_request_token
        )

        cfn = session.resource('cloudformation')
        stack = cfn.Stack(parameters['StackName'])
        if self.options.no_wait:
            self.ppt.secho('ChangeSet execution started.')
        else:
            if is_new_stack:
                self.ppt.wait_until_deploy_complete(session, stack, self.options.disable_tail_events)
            else:
                self.ppt.wait_until_update_complete(session, stack, self.options.disable_tail_events)
            self.ppt.secho('ChangeSet execution complete.', fg='green')

    @backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def create_change_set(self, client, parameters):
        return client.create_change_set(**parameters)

    @backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def describe_change_set(self, client, changeset_name, parameters):
        return client.describe_change_set(
            ChangeSetName=changeset_name,
            StackName=parameters['StackName'],
        )

    @backoff.on_exception(backoff.expo, botocore.exceptions.ClientError, max_tries=10,
                          giveup=is_not_rate_limited_exception)
    def check_changeset_type(self, client, parameters):
        try:
            # check whether stack is already created.
            status = client.describe_stacks(StackName=parameters['StackName'])
            stack_status = status['Stacks'][0]['StackStatus']
        except botocore.exceptions.ClientError as e:

            if is_rate_limited_exception(e):
                # stack might exist but we got Throttling error, retry is needed so rerasing exception
                raise
            # stack not yet created
            is_new_stack = True
            changeset_type = 'CREATE'
        else:
            if stack_status == 'REVIEW_IN_PROGRESS':
                # first ChangeSet execution failed, create "new stack" changeset again
                is_new_stack = True
                changeset_type = 'CREATE'
            else:
                # updating an existing stack
                is_new_stack = False
                changeset_type = 'UPDATE'
        return changeset_type, is_new_stack
