import pytest

from makeapp.exceptions import CommandError, ProjectorExeption
from makeapp.helpers.dist import DistHelper
from makeapp.helpers.tests import TestsHelper as MatrixTestsHelper
from makeapp.helpers.vcs import GitHelper
from makeapp.utils import Uv, run_command


def test_disthelper():
    assert DistHelper


class TestTestsHelper:

    def test_get_matrix_github(self, datafix_dir):
        assert MatrixTestsHelper.get_matrix_github(datafix_dir / 'github_matrix.yml') == [
            {'django-version': 2.0, 'python-version': '3.10'},
            {'django-version': 3.0, 'python-version': '3.10'},
            {'django-version': 4.0, 'python-version': '3.10'},
            {'django-version': 5.0, 'python-version': '3.10'},
            {'django-version': 2.0, 'python-version': 3.11},
            {'django-version': 3.0, 'python-version': 3.11},
            {'django-version': 4.0, 'python-version': 3.11},
            {'django-version': 5.0, 'python-version': 3.11},
            {'django-version': 3.0, 'python-version': 3.12},
            {'django-version': 4.0, 'python-version': 3.12},
            {'django-version': 5.0, 'python-version': 3.12},
            {'django-version': 6.0, 'python-version': 3.12},
            {'django-version': 5.0, 'python-version': 3.14},
            {'django-version': 6.0, 'python-version': 3.14}
        ]

    def test_apply_context(self):
        apply = MatrixTestsHelper.apply_context
        assert apply(
            'a${{django-version}}b && |${{ python }}|',
            {'django-version': 2.0, 'python': '3.10'}
        ) == 'a2.0b && |3.10|'

    def test_get_matrix_prefers_conventional_test_job(self, tmp_path):
        workflow = tmp_path / 'workflow.yml'
        workflow.write_text(
            'jobs:\n'
            '  lint: {strategy: {matrix: {os: [linux]}}}\n'
            '  build: {strategy: {matrix: {python-version: [3.11]}}}\n'
            '  tests: {strategy: {matrix: {python-version: [3.12]}}}\n'
        )

        assert MatrixTestsHelper.get_matrix_github(workflow) == [
            {'python-version': 3.12},
        ]

    def test_get_matrix_rejects_workflow_without_python_matrix(self, tmp_path):
        workflow = tmp_path / 'workflow.yml'
        workflow.write_text('jobs: {lint: {strategy: {matrix: {os: [linux]}}}}')

        with pytest.raises(ProjectorExeption, match='No test matrix'):
            MatrixTestsHelper.get_matrix_github(workflow)


def test_run_command_does_not_interpret_shell_syntax():
    marker = 'value; echo injected'

    assert run_command(['printf', '%s', marker]) == [marker]


def test_git_remote_is_passed_as_single_argument(monkeypatch):
    issued = []
    monkeypatch.setattr('makeapp.helpers.vcs.run_command', issued.append)

    GitHelper().add_remote('https://example.test/repo;echo-injected')

    assert issued == [[
        'git',
        'remote',
        'add',
        'origin',
        'https://example.test/repo;echo-injected',
    ]]


def test_git_accepts_unborn_main_branch(in_tmp_path):
    run_command(['git', 'init', '-q', '-b', 'main'])

    helper = GitHelper()

    helper.check()
    assert helper.get_current_branch() == 'main'


def test_git_push_uses_current_branch(monkeypatch):
    issued = []
    helper = GitHelper()

    def run(args):
        if args[0] == 'symbolic-ref':
            return ['feature']
        issued.append(args)
        return []

    monkeypatch.setattr(helper, 'run_command', run)

    helper.push(upstream=True)

    assert issued == [
        ['push', '-u', 'origin', 'feature'],
        ['push', '--tags'],
    ]


def test_uv_is_checked_when_used(monkeypatch):
    monkeypatch.setattr('makeapp.utils.shutil.which', lambda command: None)

    with pytest.raises(CommandError, match="Failed to execute 'uv'"):
        Uv.sync()
