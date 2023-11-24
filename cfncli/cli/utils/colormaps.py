"""Status string to click.style mapping"""

_STACK_STATUS_TO_COLOR = {
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_FAILED': dict(fg='red'),
    'CREATE_COMPLETE': dict(fg='green'),
    'ROLLBACK_IN_PROGRESS': dict(fg='yellow'),
    'ROLLBACK_FAILED': dict(fg='red'),
    'ROLLBACK_COMPLETE': dict(fg='red'),
    'DELETE_IN_PROGRESS': dict(fg='yellow'),
    'DELETE_FAILED': dict(fg='red'),
    'DELETE_SKIPPED': dict(fg='red'),
    'DELETE_COMPLETE': dict(fg='green'),
    'UPDATE_IN_PROGRESS': dict(fg='yellow'),
    'UPDATE_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='green'),
    'UPDATE_COMPLETE': dict(fg='green'),
    'UPDATE_ROLLBACK_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_FAILED': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS': dict(fg='red'),
    'UPDATE_ROLLBACK_COMPLETE': dict(fg='green'),
    'UPDATE_FAILED': dict(fg='red'),
    'REVIEW_IN_PROGRESS': dict(fg='yellow'),
    'IMPORT_FAILED': dict(fg='red'),
    'IMPORT_COMPLETE': dict(fg='green'),
    'IMPORT_IN_PROGRESS': dict(fg='yellow'),
    'IMPORT_ROLLBACK_IN_PROGRESS': dict(fg='red'),
    'IMPORT_ROLLBACK_FAILED': dict(fg='red'),
    'IMPORT_ROLLBACK_COMPLETE': dict(fg='red'),
    # custom status:
    'STACK_NOT_FOUND': dict(fg='red')
}

_CHANGESET_STATUS_TO_COLOR = {
    'UNAVAILABLE': dict(fg='white', dim=True),
    'AVAILABLE': dict(fg='green'),
    'EXECUTE_IN_PROGRESS': dict(fg='yellow'),
    'EXECUTE_COMPLETE': dict(fg='green'),
    'EXECUTE_FAILED': dict(fg='red'),
    'OBSOLETE': dict(fg='white', dim=True),

    'CREATE_PENDING': dict(fg='yellow'),
    'CREATE_IN_PROGRESS': dict(fg='yellow'),
    'CREATE_COMPLETE': dict(fg='green'),
    'DELETE_COMPLETE': dict(fg='green'),
    'FAILED': dict(fg='red'),
}

_CHANGESET_ACTION_TO_COLOR = {
    'Add': dict(fg='green'),
    'Modify': dict(fg='yellow'),
    'Remove': dict(fg='red'),
}

_CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR = {
    'Never': dict(fg='green'),
    'Conditionally': dict(fg='yellow'),
    'Always': dict(fg='red'),
}

_CHANGESET_REPLACEMENT_TO_COLOR = {
    'True': dict(fg='red'),
    'Conditional': dict(fg='yellow'),
    'False': dict(fg='green'),
}

_DRIFT_STATUS_TO_COLOR = {
    'DELETED': dict(fg='red'),
    'MODIFIED': dict(fg='yellow'),
    'NOT_CHECKED': dict(fg='white', dim=True),
    'IN_SYNC': dict(fg='green'),
    'UNKNOWN': dict(fg='white', dim=True),
    'DRIFTED': dict(fg='red'),
    'DETECTION_IN_PROGRESS': dict(fg='yellow'),
    'DETECTION_FAILED': dict(fg='red'),
    'DETECTION_COMPLETE': dict(fg='green'),
}


class ColorMap:
    """Return a default colormap when status missing from mapping."""

    def __init__(self, mapping):
        self._mapping = mapping

    def __getitem__(self, status):
        try:
            return self._mapping[status]
        except KeyError:
            return dict()


STACK_STATUS_TO_COLOR = ColorMap(_STACK_STATUS_TO_COLOR)
CHANGESET_STATUS_TO_COLOR = ColorMap(_CHANGESET_STATUS_TO_COLOR)
CHANGESET_ACTION_TO_COLOR = ColorMap(_CHANGESET_ACTION_TO_COLOR)
CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR = ColorMap(
    _CHANGESET_RESOURCE_REPLACEMENT_TO_COLOR)
CHANGESET_REPLACEMENT_TO_COLOR = ColorMap(_CHANGESET_REPLACEMENT_TO_COLOR)
DRIFT_STATUS_TO_COLOR = ColorMap(_DRIFT_STATUS_TO_COLOR)
