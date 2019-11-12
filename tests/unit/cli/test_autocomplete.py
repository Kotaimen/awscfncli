import os

from awscfncli2.cli.autocomplete import stack_auto_complete
from awscfncli2.config import ANNOTATED_SAMPLE_CONFIG


def test_stack_auto_complete(tmp_path):
    os.chdir(tmp_path)
    f = tmp_path / "cfn-cli.yaml"
    f.write_text(ANNOTATED_SAMPLE_CONFIG)
    assert stack_auto_complete(None, [], "") == [("Develop.Table", "ddb-table")]
