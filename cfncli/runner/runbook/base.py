# -*- coding: utf-8 -*-


class RunBookError(Exception):
    pass


class StackDeploymentContext:
    @property
    def stack_key(self):
        raise NotImplementedError

    @property
    def session(self):
        raise NotImplementedError

    @property
    def metadata(self):
        raise NotImplementedError

    @property
    def parameters(self):
        raise NotImplementedError


class RunBook:
    def __init__(self):
        self._contexts = list()

    @property
    def contexts(self):
        return self._contexts

    def pre_run(self, command, context):
        pass

    def post_run(self, command, context):
        pass

    def run(self, command, rev=False):
        if rev:
            stack_contexts = reversed(self.contexts)
        else:
            stack_contexts = self.contexts

        for context in stack_contexts:
            self.pre_run(command, context)
            command.run(context)
            self.post_run(command, context)
