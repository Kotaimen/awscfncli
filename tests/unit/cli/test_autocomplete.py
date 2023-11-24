import os

from cfncli.cli.autocomplete import stack_auto_complete
from cfncli.config import ANNOTATED_SAMPLE_CONFIG


def test_stack_auto_complete(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "cfn-cli.yaml"
    f.write_text(ANNOTATED_SAMPLE_CONFIG)
    assert stack_auto_complete(None, [], "") == [("Develop.Table", "ddb-table")]
