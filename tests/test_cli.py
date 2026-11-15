import logging
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest
from click.testing import CliRunner

from makeapp.apptools import Project
from makeapp.cli import entry_point, main
from makeapp.exceptions import AppMakerException
from makeapp.helpers.github import GithubHelper
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


def test_version_does_not_require_uv():
    env = {**os.environ, 'PATH': ''}

    result = subprocess.run(
        [sys.executable, '-m', 'makeapp.cli', '--version'],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert result.returncode == 0
    assert ', version ' in result.stdout


def test_uv_command_fails_when_uv_is_missing():
    env = {**os.environ, 'PATH': ''}

    result = subprocess.run(
        [sys.executable, '-m', 'makeapp.cli', 'up'],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert result.returncode == 1
    assert "Failed to execute 'uv' command" in result.stderr


def test_release_no_prompt_non_interactive(run_command, monkeypatch):
    """`release --no-prompt` must not ask for confirmations."""

    calls = []
    project_mock = type("ProjectMock", (), {
        "pull": lambda self: calls.append("pull"),
        "get_release_info": lambda self, increment: ("1.0.1", "summary"),
        "release": lambda self, version, summary: calls.append("release"),
        "publish": lambda self: calls.append("publish"),
        "package": type("P", (), {"version_current_str": "1.0.0", "version_next_str": "1.0.1"})(),
    })
    monkeypatch.setattr("makeapp.cli.Project", lambda **kwargs: project_mock())

    result = run_command(["release", "--no-prompt"])

    assert result.exit_code == 0
    assert calls == ["pull", "release", "publish"]


def test_new_github_repo_creation(in_tmp_path, monkeypatch):
    created = []
    monkeypatch.setattr(GithubHelper, 'is_available', lambda *args: True)
    monkeypatch.setattr(
        GithubHelper, 'create_repo',
        lambda self, name, *, private: created.append((name, private)) or 'https://x')

    # Prompts: skip name check, rollout, init repo, create GitHub repo (yes),
    # make it public (yes), init venv (yes).
    result = CliRunner().invoke(entry_point, ['new', 'someapp', '.'], obj={}, input='\n\n\ny\n\n\n')

    assert result.exit_code == 0
    assert created == [('someapp', False)]


def test_new_github_repo_already_exists(in_tmp_path, monkeypatch):
    linked = []
    monkeypatch.setattr(GithubHelper, 'is_available', lambda *args: True)
    monkeypatch.setattr(GithubHelper, 'repo_exists', lambda self, name: True)
    monkeypatch.setattr(
        GithubHelper, 'link_repo', lambda self, name: linked.append(name))
    monkeypatch.setattr(
        GithubHelper, 'create_repo',
        lambda self, name, *, private: (_ for _ in ()).throw(AssertionError('should not create')))

    result = CliRunner().invoke(entry_point, ['new', 'someapp', '.'], obj={}, input='\n\n\ny\n\n\n')

    assert result.exit_code == 0
    assert 'already exists' in result.output
    assert linked == ['someapp']


def test_release_warns_on_breaking_with_nonmajor(run_command, monkeypatch):
    def fake_gather(self):
        self.package = SimpleNamespace(version_current_str='1.2.0', version_next_str='1.3.0')
        self.changelog = SimpleNamespace(deduce_version_increment=lambda: 'minor')

    monkeypatch.setattr(Project, '_gather_data', fake_gather)
    monkeypatch.setattr(Project, 'pull', lambda self: None)
    monkeypatch.setattr(
        Project, 'get_release_info',
        lambda self, increment=None: (self._gather_data() or ('v1.3.0', '* !! Breaking change.')))

    released = []
    monkeypatch.setattr(Project, 'release', lambda self, v, s: released.append(v))
    monkeypatch.setattr(Project, 'publish', lambda self: None)

    # Decline at the breaking warning prompt.
    result = CliRunner().invoke(entry_point, ['release'], obj={}, input='n\n')
    assert 'breaking changes are present' in result.output
    assert not released

    # Confirm at the warning, then proceed.
    result = CliRunner().invoke(entry_point, ['release'], obj={}, input='y\ny\nn\n')
    assert 'breaking changes are present' in result.output
    assert released == ['v1.3.0']

    # Non-interactive mode: warning shown, no prompt.
    released.clear()
    result = run_command(['release', '--no-prompt'])
    assert 'breaking changes are present' in result.output
    assert released == ['v1.3.0']


def test_docs_group_serves_by_default(run_command, monkeypatch):
    calls = []
    monkeypatch.setattr(Project, 'docs', lambda self, serve: calls.append(serve))

    result = run_command(['docs'])
    assert result.exit_code == 0
    assert calls == [True]

    result = run_command(['docs', '-b'])
    assert result.exit_code == 0
    assert calls == [True, False]


def test_docs_check_command(run_command, monkeypatch):
    monkeypatch.setattr(Project, 'docs_check', lambda self: [])

    result = run_command(['docs', 'check'])
    assert result.exit_code == 0
    assert 'Done' in result.output

    monkeypatch.setattr(Project, 'docs_check', lambda self: ['docs/x.md:1: https://dead.example/'])

    result = run_command(['docs', 'check'])
    assert result.exit_code == 1
    assert 'https://dead.example/' in result.output


def test_check_gate(run_command, monkeypatch):
    monkeypatch.setattr(Project, 'check', lambda self: [])

    result = run_command(['check'])
    assert result.exit_code == 0
    assert 'Done' in result.output

    monkeypatch.setattr(Project, 'check', lambda self: ['Tests failed: py314'])

    result = run_command(['check'])
    assert result.exit_code == 1
    assert 'Tests failed' in result.output
