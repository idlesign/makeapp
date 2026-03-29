import logging

import pytest
from click.testing import CliRunner

from makeapp.cli import entry_point


@pytest.fixture
def run_command():
    def run_command_(args: list[str]):
        runner = CliRunner()
        return runner.invoke(entry_point, args, obj={})
    return run_command_


def test_smoke(run_command):

    result = run_command(['--version'])
    assert ", version " in result.output
    assert result.exit_code == 0


def test_smallcycle(in_tmp_path, run_command, caplog):

    caplog.at_level(logging.DEBUG, logger='makeapp')

    result = run_command(['new', '--no-prompt', 'some', '.'])
    assert 'Done' in result.output

    result = run_command(['tests'])
    assert 'Running tests' in caplog.text
    assert "Tests OK" in result.output
    assert result.exit_code == 0
