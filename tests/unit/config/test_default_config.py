import os
import pathlib

from cfncli.config import find_default_config


def test_default_config_empty(tmp_path):
    os.chdir(tmp_path)
    # Current behaviour is return "cfn-cli.yml" when the file does not exist.
    assert find_default_config() == "cfn-cli.yml"


def test_default_config_file1(tmp_path):
    f = tmp_path / "cfn-cli.yaml"
    f.touch()
    os.chdir(tmp_path)
    assert find_default_config() == "cfn-cli.yaml"


def test_default_config_file2(tmp_path):
    f = tmp_path / "cfn-cli.yml"
    f.touch()
    os.chdir(tmp_path)
    assert find_default_config() == "cfn-cli.yml"


def test_default_config_file3(tmp_path):
    f1 = tmp_path / "cfn-cli.yaml"
    f1.touch()
    f2 = tmp_path / "cfn-cli.yml"
    f2.touch()
    os.chdir(tmp_path)
    assert find_default_config() == "cfn-cli.yaml"


def test_default_config_dir1(tmp_path):
    d = tmp_path / "config"
    d.mkdir()
    f = d / "cfn-cli.yaml"
    f.touch()
    os.chdir(tmp_path)
    assert find_default_config("config") == "config/cfn-cli.yaml"
