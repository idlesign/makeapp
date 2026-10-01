import logging

import pytest
from click.testing import CliRunner

from makeapp.cli import entry_point, main
from makeapp.exceptions import AppMakerException
from makeapp.helpers.tests import TestsHelper as MatrixTestsHelper


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

    result = run_command(['tests', '--only', 'py314'])
    assert 'Running tests' in caplog.text
    assert "Tests OK" in result.output
    assert result.exit_code == 0


def test_tests_failure_returns_nonzero(run_command, monkeypatch):
    monkeypatch.setattr(
        'makeapp.cli.Project.run_tests',
        lambda *args, **kwargs: {MatrixTestsHelper.KEY_OK: [], MatrixTestsHelper.KEY_FAIL: ['py314']},
    )

    result = run_command(['tests'])

    assert 'Tests FAIL' in result.output
    assert 'Done' not in result.output
    assert result.exit_code == 1


def test_tests_empty_selection_returns_nonzero(run_command, monkeypatch):
    monkeypatch.setattr(
        'makeapp.cli.Project.run_tests',
        lambda *args, **kwargs: {MatrixTestsHelper.KEY_OK: [], MatrixTestsHelper.KEY_FAIL: []},
    )

    result = run_command(['tests'])

    assert 'No test environments were run.' in result.output
    assert result.exit_code == 1


def test_main_returns_nonzero_on_domain_error(monkeypatch, capsys):
    def fail(**kwargs):
        raise AppMakerException('Failure')

    monkeypatch.setattr('makeapp.cli.entry_point', fail)

    with pytest.raises(SystemExit) as exc_info:
        main()

    assert exc_info.value.code == 1
    assert 'Failure' in capsys.readouterr().err
