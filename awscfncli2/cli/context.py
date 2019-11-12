"""Click context object.

Options - data object contains options from main cli
ContextBuilder - build context from given options

Context - click context object,
"""
import os
import threading
from collections import namedtuple

from awscfncli2.config import load_config, find_default_config
from awscfncli2.runner import Boto3Profile, Boto3RunBook, StackSelector
from .utils.pprint import StackPrettyPrinter


class Options(namedtuple(
    'Options',
    [
        'config_filename',
        'stack_selector',
        'profile_name',
        'region_name',
        'artifact_store',
        'verbosity',
    ]
)):
    pass


class ContextBuilder:
    """Build Context from given Options."""

    def __init__(self, options: Options):
        self._opt = options

    def build(self):
        """Build Context from given Options.

        A new Context object is returned every time.
        """
        raise NotImplementedError


class Context:
    """Click context object


    # Manage config parsing, transforming deployment process.
    """

    def __init__(self,
                 config_filename: str,
                 artifact_store: str,
                 pretty_printer: StackPrettyPrinter,
                 stack_selector: StackSelector,
                 boto3_profile: Boto3Profile,
                 builder,
                 ):
        # simple
        self._config_filename: str = config_filename
        self._artifact_store: str = artifact_store
        # complex
        self._pretty_printer: StackPrettyPrinter = pretty_printer
        self._stack_selector = stack_selector
        self._boto3_profile = boto3_profile
        # lazy-loaded
        self._deployments = None
        self._command_runner = None

        # internals
        self.__builder = builder
        self.__lock = threading.RLock()

    @property
    def config_filename(self):
        """Config file name"""
        return self._config_filename

    @property
    def stack_selector(self):
        """Stack selector"""
        return self._stack_selector

    @property
    def boto3_profile(self):
        """Boto3 session profiles"""
        return self._boto3_profile

    @property
    def verbosity(self):
        """Verbosity level"""
        return self._pretty_printer.verbosity

    @property
    def ppt(self):
        """CLI pretty printer"""
        return self._pretty_printer

    @property
    def deployments(self):
        """Stack deployment spec."""
        # XXX: Lazy-loading so we don't get error if user is just looking at help
        with self.__lock:
            if self._deployments is None:
                self._deployments = self.__builder.parse_config(self.config_filename)
        return self._deployments

    @property
    def runner(self):
        """Command runner."""
        with self.__lock:
            if self._command_runner is None:
                self._command_runner = self.__builder.build_runner(
                    self.boto3_profile,
                    self._artifact_store,
                    self.deployments,
                    self.stack_selector,
                    self.ppt
                )
        return self._command_runner


class DefaultContextBuilder(ContextBuilder):
    """Default context builder."""

    def build(self) -> Context:
        config_filename = find_default_config(self._opt.config_filename)

        stack_selector = StackSelector(self._opt.stack_selector)

        boto3_profile = Boto3Profile(profile_name=self._opt.profile_name,
                                     region_name=self._opt.region_name)

        pretty_printer = StackPrettyPrinter(verbosity=self._opt.verbosity)

        context = Context(
            config_filename=config_filename,
            stack_selector=stack_selector,
            boto3_profile=boto3_profile,
            pretty_printer=pretty_printer,
            artifact_store=self._opt.artifact_store,
            builder=self)

        return context

    @staticmethod
    def parse_config(config_filename):
        """Parse configuration file from options."""
        return load_config(config_filename)

    @staticmethod
    def build_runner(boto3_profile, artifact_store, deployments, stack_selector, pretty_printer):
        """Build command runner from options."""
        return Boto3RunBook(
            boto3_profile,
            artifact_store,
            deployments,
            stack_selector,
            pretty_printer
        )
