import pytest
import requests

from makeapp.exceptions import CommandError, ProjectorException
from makeapp.helpers.dist import DistHelper
from makeapp.helpers.docs import DocsHelper
from makeapp.helpers.github import GithubHelper
from makeapp.helpers.tests import TestsHelper as MatrixTestsHelper
from makeapp.helpers.vcs import GitHelper, VcsHelper
from makeapp.helpers.venvs import VenvHelper
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

        with pytest.raises(ProjectorException, match='No test matrix'):
            MatrixTestsHelper.get_matrix_github(workflow)

    def test_run_tests_reuses_matching_venv_with_matrix_deps(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(VenvHelper, 'read_python_version', staticmethod(lambda venv_path: (3, 14)))

        helper = MatrixTestsHelper(
            settings={'deps': ['django~=${{ django-version }}']},
        )
        monkeypatch.setattr(helper, 'get_matrix_github', lambda path: [{
            'python-version': 3.14,
            'django-version': '6.0',
        }])
        issued = []
        monkeypatch.setattr(
            'makeapp.helpers.tests.Uv.exec',
            lambda command, env=None: issued.append((command, env)),
        )

        assert helper.run_tests() == {
            helper.KEY_OK: ['py314_django60'],
            helper.KEY_FAIL: [],
        }
        assert issued == [(
            [
                'run',
                '--no-sync',
                '--group',
                'tests',
                '--python',
                '3.14',
                '--with',
                'django~=6.0',
                'pytest',
            ],
            {
                'VIRTUAL_ENV': '.venv',
                'UV_PROJECT_ENVIRONMENT': '.venv',
            },
        )]

    def test_run_tests_reuses_matching_venv_after_only_filter(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(VenvHelper, 'read_python_version', staticmethod(lambda venv_path: (3, 14)))

        helper = MatrixTestsHelper(settings={}, only=['py314'])
        monkeypatch.setattr(helper, 'get_matrix_github', lambda path: [
            {'python-version': 3.13},
            {'python-version': 3.14},
        ])
        issued = []
        monkeypatch.setattr(
            'makeapp.helpers.tests.Uv.exec',
            lambda command, env=None: issued.append((command, env)),
        )

        assert helper.run_tests() == {
            helper.KEY_OK: ['py314'],
            helper.KEY_FAIL: [],
        }
        assert issued == [(
            ['run', '--no-sync', '--group', 'tests', '--python', '3.14', 'pytest'],
            {
                'VIRTUAL_ENV': '.venv',
                'UV_PROJECT_ENVIRONMENT': '.venv',
            },
        )]

    def test_run_tests_keeps_isolation_for_incompatible_venv(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        monkeypatch.setattr(VenvHelper, 'read_python_version', staticmethod(lambda venv_path: (3, 13)))

        helper = MatrixTestsHelper(settings={})
        monkeypatch.setattr(
            helper,
            'get_matrix_github',
            lambda path: [{'python-version': 3.14}],
        )
        issued = []
        monkeypatch.setattr(
            'makeapp.helpers.tests.Uv.exec',
            lambda command, env=None: issued.append((command, env)),
        )

        assert helper.run_tests() == {
            helper.KEY_OK: ['py314'],
            helper.KEY_FAIL: [],
        }
        environment = {
            'VIRTUAL_ENV': '.venv_ma/py314',
            'UV_PROJECT_ENVIRONMENT': '.venv_ma/py314',
        }
        assert issued == [
            (
                ['sync', '--only-group', 'tests', '--python', '3.14'],
                environment,
            ),
            (
                ['pip', 'install', '-e', '.', '--python', '.venv_ma/py314'],
                environment,
            ),
            (['run', '--no-sync', 'pytest'], environment),
        ]


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
        ['push', '--follow-tags'],
    ]


def test_uv_is_checked_when_used(monkeypatch):
    monkeypatch.setattr('makeapp.utils.shutil.which', lambda command: None)

    with pytest.raises(CommandError, match="Failed to execute 'uv'"):
        Uv.sync()


def test_venv_register_tool_passes_separate_arguments(tmp_path, monkeypatch):
    issued = []
    monkeypatch.setattr('makeapp.helpers.venvs.Uv.exec', issued.append)

    VenvHelper(tmp_path).register_tool()

    assert issued == [['tool', 'install', '--force', '--editable', '.']]


class TestGitModified:

    def test_get_modified(self, in_tmp_path):
        helper = GitHelper()
        run_command(['git', 'init', '-q'])

        # Untracked files are not modifications.
        (in_tmp_path / 'untracked.txt').write_text('1')
        assert helper.get_modified() == []

        tracked = in_tmp_path / 'tracked.txt'
        tracked.write_text('1')
        run_command(['git', 'add', '.'])
        run_command(['git', 'commit', '-qm', 'initial'])

        # Unstaged modification.
        tracked.write_text('2')
        assert helper.get_modified() == ['tracked.txt']

        # Staged modification.
        run_command(['git', 'add', 'tracked.txt'])
        assert helper.get_modified() == ['tracked.txt']

        # Deletion is not a modification.
        tracked.unlink()
        assert helper.get_modified() == []

    def test_get_modified_path_with_spaces(self, in_tmp_path):
        helper = GitHelper()
        run_command(['git', 'init', '-q'])

        tracked = in_tmp_path / 'my file.txt'
        tracked.write_text('1')
        run_command(['git', 'add', '.'])
        run_command(['git', 'commit', '-qm', 'initial'])

        tracked.write_text('2')
        run_command(['git', 'add', 'my file.txt'])
        assert helper.get_modified() == ['my file.txt']

    def test_add_all(self, in_tmp_path):
        helper = GitHelper()
        run_command(['git', 'init', '-q'])

        (in_tmp_path / 'some.txt').write_text('1')

        VcsHelper.add(helper)

        assert 'some.txt' in helper.get_modified() or \
            'A  some.txt' in run_command(['git', 'status', '-s'])


class TestGithubHelper:

    def test_get_repo_slug(self, monkeypatch):
        helper = GithubHelper(GitHelper())

        monkeypatch.setattr(helper.vcs, 'run_command', lambda args: ['git@github.com:owner/repo.git'])
        assert helper.get_repo_slug() == 'owner/repo'

        monkeypatch.setattr(helper.vcs, 'run_command', lambda args: ['https://github.com/owner/repo.git'])
        assert helper.get_repo_slug() == 'owner/repo'

        monkeypatch.setattr(helper.vcs, 'run_command', lambda args: ['git@gitlab.com:owner/repo.git'])
        assert helper.get_repo_slug() is None

    def test_create_release(self, monkeypatch):
        issued = []
        monkeypatch.setattr(
            'makeapp.helpers.github.run_command', lambda args: issued.append(args) or ['https://x'])
        monkeypatch.setattr(GithubHelper, 'get_latest_tag', lambda self: 'v1.0.0')

        helper = GithubHelper(GitHelper())
        url = helper.create_release()

        assert issued == [['gh', 'release', 'create', 'v1.0.0', '--title', 'v1.0.0', '--notes-from-tag']]
        assert url == 'https://x'

    def test_create_repo(self, monkeypatch):
        issued = []
        monkeypatch.setattr('makeapp.helpers.github.run_command', lambda args: issued.append(args) or ['https://x'])

        helper = GithubHelper(GitHelper())
        url = helper.create_repo('myapp', private=False)

        assert issued == [['gh', 'repo', 'create', 'myapp', '--public', '--source', '.', '--push']]
        assert url == 'https://x'

    def test_repo_exists(self, monkeypatch):
        helper = GithubHelper(GitHelper())

        monkeypatch.setattr('makeapp.helpers.github.run_command', lambda args: ['ok'])
        assert helper.repo_exists('myapp') is True

        def fail(args):
            raise CommandError('not found')

        monkeypatch.setattr('makeapp.helpers.github.run_command', fail)
        assert helper.repo_exists('myapp') is False

    def test_link_repo(self, monkeypatch, in_tmp_path):
        run_command(['git', 'init', '-q', '-b', 'main'])

        monkeypatch.setattr(
            'makeapp.helpers.github.run_command',
            lambda args: ['git@github.com:owner/myapp.git'])

        issued = []
        helper = GithubHelper(GitHelper())
        monkeypatch.setattr(helper.vcs, 'run_command', lambda args: issued.append(args) or ['main'])

        helper.link_repo('myapp')

        assert issued == [
            ['remote', 'add', 'origin', 'git@github.com:owner/myapp.git'],
            ['symbolic-ref', '--quiet', '--short', 'HEAD'],
            ['push', '-u', 'origin', 'main'],
            ['push', '--follow-tags'],
        ]


class TestDocsHelper:

    def test_check_links(self, tmp_path, monkeypatch):
        docs = tmp_path / 'docs'
        docs.mkdir()
        (docs / 'page.md').write_text(
            'See [good](https://good.example/) and <https://bad.example/page>.\n'
            'Plain https://ok.example/path, mention.\n')

        statuses = {
            'https://good.example/': 200,
            'https://ok.example/path': 200,
            'https://bad.example/page': 404,
        }

        class FakeResponse:
            def __init__(self, status_code):
                self.status_code = status_code

        monkeypatch.setattr(
            'makeapp.helpers.docs.requests.head',
            lambda url, **kwargs: FakeResponse(statuses[url]))

        problems = DocsHelper.check_links(docs)

        assert len(problems) == 1
        assert 'https://bad.example/page' in problems[0]

    def test_is_url_alive_fallback(self, monkeypatch):
        calls = []

        class FakeResponse:
            status_code = 405

        monkeypatch.setattr(
            'makeapp.helpers.docs.requests.head',
            lambda url, **kwargs: calls.append('head') or FakeResponse())
        monkeypatch.setattr(
            'makeapp.helpers.docs.requests.get',
            lambda url, **kwargs: calls.append('get') or FakeResponse())

        assert DocsHelper.is_url_alive('https://x.example/') is False
        assert calls == ['head', 'get']

    def test_is_url_alive_connection_error(self, monkeypatch):
        def fail(url, **kwargs):
            raise requests.ConnectionError('no route')

        monkeypatch.setattr('makeapp.helpers.docs.requests.head', fail)

        assert DocsHelper.is_url_alive('https://x.example/') is False
