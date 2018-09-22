from ...cli.utils import StackPrettyPrinter


class Command(object):

    def __init__(self, pretty_printer, options):
        assert isinstance(pretty_printer, StackPrettyPrinter)
        self.ppt = pretty_printer
        self.options = options
