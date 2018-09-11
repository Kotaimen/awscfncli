from collections import namedtuple

from ...cli.utils import StackPrettyPrinter


class StackDeployOptions(namedtuple('StackDeployOptions',
                         ['no_wait', 'on_failure'])):
    pass


class StackDeployCommand(object):

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        assert isinstance(options, StackDeployOptions)
        self.ppt = pretty_printer
        self.options = options

    def run(self, session, parameters, metadata):
        self.ppt.pprint_stack_name(metadata['StackKey'])

        cfn = session.resource('cloudformation')

        self.ppt.pprint_session(session)

        # force on failure option
        if self.options.on_failure is not None:
            parameters.pop('DisableRollback', None)
            parameters['OnFailure'] = self.options.on_failure

        self.ppt.pprint_stack_parameters(parameters)

        # call boto3
        stack = cfn.create_stack(**parameters)
        self.ppt.pprint_stack(stack)

        # wait until deployment complete
        if self.options.no_wait:
            return

        self.ppt.wait_until_deploy_complete(session, stack)
