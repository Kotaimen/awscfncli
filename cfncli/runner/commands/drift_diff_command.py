from collections import namedtuple

from .command import Command


class DriftDiffOptions(namedtuple('DriftDiffOptions',
                                  [])):
    pass


class DriftDiffCommand(Command):
    SKIP_UPDATE_REFERENCES = True

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        self.ppt.pprint_stack_name(stack_context.stack_key,
                                   parameters['StackName'],
                                   'Describing drift of ')

        # create boto3 client
        self.ppt.pprint_session(session)
        self.ppt.pprint_parameters(parameters)

        client = session.client('cloudformation')

        # call boto3
        self.ppt.secho('Drifted resources:')
        response = client.describe_stack_resource_drifts(
            StackName=parameters['StackName'],
            StackResourceDriftStatusFilters=['MODIFIED','DELETED']
        )

        for drift in response['StackResourceDrifts']:
            self.ppt.pprint_resource_drift(drift)
