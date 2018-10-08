import fnmatch
import six


class StackSelector(object):
    """Check whether stack according to sepcified patten"""

    def __init__(self, stack_selector):

        split = stack_selector.rsplit('.', 1)

        if len(split) == 1:
            self.stage_pattern = '*'
            self.stack_pattern = stack_selector
        else:
            self.stage_pattern = split[0]
            self.stack_pattern = split[1]

    def matches(self, qualified_name):
        if isinstance(qualified_name, six.string_types):
            qualified_name = tuple(qualified_name.split('.'))

        stage_name, stack_name = qualified_name

        return fnmatch.fnmatchcase(stage_name, self.stage_pattern) and \
               fnmatch.fnmatchcase(stack_name, self.stack_pattern)

    def __repr__(self):
        return '{}({}.{})'.format(self.__class__.__name__, self.stage_pattern,
                                  self.stack_pattern)
