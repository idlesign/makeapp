from makeapp.helpers.dist import DistHelper
from makeapp.helpers.tests import TestsHelper as MatrixTestsHelper
from makeapp.helpers.vcs import GitHelper
from makeapp.utils import run_command


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
