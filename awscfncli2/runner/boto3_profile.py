import boto3


class Boto3Profile(object):
    """Store parameters for creating a boto3 profile"""

    def __init__(self, profile_name, region_name):
        self.profile_name = profile_name
        self.region_name = region_name

    def update(self, other):
        """Update profile with value from another one"""
        assert isinstance(other, Boto3Profile)
        if other.profile_name:
            self.profile_name = other.profile_name
        if other.region_name:
            self.region_name = other.region_name

    def get_boto3_session(self):
        # XXX: caching session object?
        return boto3.Session(
            profile_name=self.profile_name,
            region_name=self.region_name,
        )

    def __repr__(self):
        return '{}({}/{})'.format(self.__class__.__name__, self.profile_name,
                                  self.region_name)
