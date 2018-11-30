import threading

from ..runner import Boto3Profile, Boto3RunBook, StackSelector
from ..config import load_config


class ClickContext(object):
    """Click context object

    Manage config parsing, transforming deployment process.
    """

    def __init__(self,
                 config_filename,
                 stack_selector,
                 profile_name,
                 region_name,
                 artifact_store,
                 pretty_printer):
        self._config_filename = config_filename
        self._stack_selector = StackSelector(stack_selector)
        self._boto3_profile = Boto3Profile(profile_name=profile_name,
                                           region_name=region_name)
        self._artifact_store = artifact_store
        self._deployments = None
        self._pretty_printer = pretty_printer
        self._runner = None

        self._lock = threading.Lock()

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
    def deployments(self):
        """Stack configurations"""
        # lazy loading the deployments so we don't get error if user is just
        # looking at command help
        with self._lock:
            if self._deployments is None:
                self._deployments = load_config(self._config_filename)
        return self._deployments

    @property
    def verbosity(self):
        return self._pretty_printer.verbosity

    @property
    def runner(self):

        if self._runner is None:
            self._runner = Boto3RunBook(
                self.boto3_profile,
                self._artifact_store,
                self.deployments,
                self.stack_selector,
                self.ppt
            )

        return self._runner

    @property
    def ppt(self):
        return self._pretty_printer
