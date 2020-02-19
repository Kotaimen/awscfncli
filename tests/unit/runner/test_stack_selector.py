from awscfncli2.runner import StackSelector


class TestStackSelector(object):

    def test_all(self):
        s = StackSelector('*')
        assert s.stage_pattern == '*'
        assert s.stack_pattern == '*'
        assert s.matches('foo.bar')
        assert s.matches('bar.baz')

    def test_matching_1(self):
        s = StackSelector('dev*.*')
        assert s.stack_pattern == '*'
        assert s.stage_pattern == 'dev*'
        assert s.matches('dev1.foo')
        assert s.matches('dev.bar')
        assert not s.matches('def.baz')

    def test_matching_2(self):
        s = StackSelector('dev?.*')
        assert s.stack_pattern == '*'
        assert s.stage_pattern == 'dev?'
        assert s.matches('dev1.foo')
        assert s.matches('dev2.bar')
        assert not s.matches('dev.bar')
