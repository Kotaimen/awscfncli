from cfncli.runner import Boto3Profile


class TestStackSelector(object):

    def test_update(self):
        s1 = Boto3Profile('foo','bar')
        s2 = Boto3Profile('foo', 'baz')
        assert s1.region_name == 'bar'
        s1.update(s2)
