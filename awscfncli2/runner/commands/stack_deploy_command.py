from collections import namedtuple
import botocore.errorfactory
from ...cli.utils import StackPrettyPrinter


class StackDeployOptions(namedtuple('StackDeployOptions',
                                    ['no_wait',
                                     'on_failure',
                                     'ignore_existing'])):
    pass


class StackDeployCommand(object):

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        assert isinstance(options, StackDeployOptions)
        self.ppt = pretty_printer
        self.options = options

    def run(self, session, parameters, metadata):
        self.ppt.pprint_stack_name(metadata['StackKey'],
                                   parameters['StackName'], 'Deploying stack ')

        cfn = session.resource('cloudformation')

        self.ppt.pprint_session(session)

        # force on failure option
        if self.options.on_failure is not None:
            parameters.pop('DisableRollback', None)
            parameters['OnFailure'] = self.options.on_failure

        self.ppt.pprint_parameters(parameters)

        # call boto3
        try:
            stack = cfn.create_stack(**parameters)
        except Exception as ex:
            if ex.__class__.__name__ == 'AlreadyExistsException' and \
                    self.options.ignore_existing:
                self.ppt.secho('Stack already exists.', fg='red')
                return
            raise

        self.ppt.pprint_stack(stack)

        # wait until deployment complete, when required
        if self.options.no_wait:
            self.ppt.secho('Stack deployment started.')
            return
        else:
            self.ppt.wait_until_deploy_complete(session, stack)
            self.ppt.secho('Stack deployment complete.', fg='green')
