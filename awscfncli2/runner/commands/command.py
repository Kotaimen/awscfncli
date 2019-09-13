from awscfncli2.cli.utils.pprint import StackPrettyPrinter


class Command(object):
    SKIP_UPDATE_REFERENCES = False

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        self.ppt = pretty_printer
        self.options = options

    def run(self, stack_context):
        raise NotImplementedError
