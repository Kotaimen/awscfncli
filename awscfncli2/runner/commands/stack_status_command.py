from collections import namedtuple

import botocore.exceptions

from ...cli.utils import StackPrettyPrinter, custom_paginator, echo_pair
from .utils import is_stack_does_not_exist_exception

class StackStatusOptions(namedtuple('StackStatusOptions',
                                    ['dry_run', 'stack_resources',
                                     'stack_exports'])):
    pass


dummy_stack = namedtuple('dummy_stack', ['stack_name', 'stack_status'])


class StackStatusCommand(object):

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        assert isinstance(options, StackStatusOptions)
        self.ppt = pretty_printer
        self.options = options

    def run(self, session, parameters, metadata):
        self.ppt.pprint_stack_name(metadata['StackKey'],
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

        # XXX: move these to pretty print proxy...

        if self.options.stack_resources:
            echo_pair('Resources')
            for r in stack.resource_summaries.all():
                echo_pair(r.logical_resource_id,
                          '(%s)' % r.resource_type,
                          indent=2, sep=' ')
                echo_pair('Status', r.resource_status,
                          indent=4)
                echo_pair('Physical ID', r.physical_resource_id, indent=4)
                echo_pair('Last Updated', r.last_updated_timestamp,
                          indent=4)

        if self.options.stack_exports:
            self.ppt.pprint_stack_parameters(stack)
            client = session.client('cloudformation')
            echo_pair('Exports')
            for export in custom_paginator(client.list_exports, 'Exports'):

                if export['ExportingStackId'] == stack.stack_id:
                    echo_pair(export['Name'], export['Value'], indent=2)
                    try:
                        for import_ in custom_paginator(client.list_imports,
                                                        'Imports',
                                                        ExportName=export[
                                                            'Name']):
                            echo_pair('Imported By', import_,
                                      value_style=dict(fg='red'), indent=4)
                    except botocore.exceptions.ClientError as e:
                        echo_pair('Export not used by any stack.',
                                  key_style=dict(fg='green'), indent=4,
                                  sep='')
