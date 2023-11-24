from collections import namedtuple

import botocore.waiter

from .command import Command

class DriftDetectOptions(namedtuple('DriftDetectOptions',
                                    ['no_wait', ])):
    pass


waiter_model = botocore.waiter.WaiterModel({
    "version": 2,
    "waiters": {
        "DriftDetectionComplete": {
            "delay": 15,
            "operation": "DescribeStackDriftDetectionStatus",
            "maxAttempts": 20,
            "acceptors": [
                {
                    "expected": "DETECTION_COMPLETE",
                    "matcher": "path",
                    "state": "success",
                    "argument": "DetectionStatus"
                },
                {
                    "expected": "DETECTION_FAILED",
                    "matcher": "path",
                    "state": "failure",
                    "argument": "DetectionStatus"
                }
            ]
        }
    }
})


class DriftDetectCommand(Command):
    SKIP_UPDATE_REFERENCES = True

    def run(self, stack_context):
        # stack contexts
        session = stack_context.session
        parameters = stack_context.parameters
        metadata = stack_context.metadata

        self.ppt.pprint_stack_name(stack_context.stack_key,
                                   parameters['StackName'],
                                   'Detecting drift of ')

        # create boto3 client
        self.ppt.pprint_session(session)
        self.ppt.pprint_parameters(parameters)

        client = session.client('cloudformation')

        # call boto3

        response = client.detect_stack_drift(StackName=parameters['StackName'])
        drift_detection_id = response['StackDriftDetectionId']

        # wait until delete complete
        if self.options.no_wait:
            self.ppt.secho('Drift detect started.')
        else:
            # create custom waiter
            waiter = botocore.waiter.create_waiter_with_client(
                'DriftDetectionComplete', waiter_model, client)
            waiter.wait(StackDriftDetectionId=drift_detection_id)

            # self.ppt.secho('Drift detection complete.', fg='green')

            result = client.describe_stack_drift_detection_status(
                StackDriftDetectionId=drift_detection_id)

            self.ppt.pprint_stack_drift(result)

            if result['DriftedStackResourceCount'] > 0:
                self.ppt.secho('Use `drift diff` command to show drifted resources.')

