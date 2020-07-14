from awscfncli2.cli.utils.colormaps import STACK_STATUS_TO_COLOR


def test_stack_status_to_color():
    assert STACK_STATUS_TO_COLOR['UPDATE_COMPLETE'] == {'fg': 'green'}
    assert STACK_STATUS_TO_COLOR['CREATE_FAILED'] == {'fg': 'red'}
    assert STACK_STATUS_TO_COLOR['IMPORT_IN_PROGRESS'] == {'fg': 'yellow'}
    # invalid status should return a empty dict instead of KeyError
    assert STACK_STATUS_TO_COLOR['FOOBAR'] == {}
