from pathlib import Path
from textwrap import dedent

import pytest

from makeapp.apptools import RELEASE_STATE_FILENAME, ChangelogData, Project
from makeapp.exceptions import ProjectorExeption
from makeapp.helpers.vcs import VcsHelper


def test_git(in_tmp_path, get_appmaker, assert_content, monkeypatch):

    get_appmaker()

    vcs = VcsHelper.get()
    vcs.commit('initial')

    project = Project()
    project.add_change(['fix1', '* change', '! warn', '+ add'])

    assert_content(in_tmp_path / 'CHANGELOG.md', [
        dedent('''
        * !! warn.
        * ++ add.
        * ++ Basic functionality.
        * ** change.
        * ** fix1.
        ''')
    ])

    version, summary = project.get_release_info()

    assert version == 'v0.1.0'
    assert summary == '* !! warn.\n* ++ add.\n* ++ Basic functionality.\n* ** change.\n* ** fix1.'

    project.release(version, summary)

    issued_commands = []

    def dummy_communicate(self, *args, **kwargs):
        issued_commands.append(self.args)
        return b'', b''

    monkeypatch.setattr('makeapp.utils.Popen.communicate', dummy_communicate)
    project.publish()

    assert issued_commands == [
        ['uv', 'build'],
        ['uv', 'publish'],
        ['git', 'push'],
        ['git', 'push', '--tags'],
    ]
    assert not (in_tmp_path / RELEASE_STATE_FILENAME).exists()


def test_publish_does_not_push_after_upload_failure(in_tmp_path, get_appmaker, monkeypatch):
    get_appmaker()
    project = Project()
    git_pushed = False

    def fail_upload():
        raise RuntimeError('upload failed')

    def push():
        nonlocal git_pushed
        git_pushed = True

    monkeypatch.setattr('makeapp.apptools.DistHelper.upload', fail_upload)
    monkeypatch.setattr(project.vcs, 'push', push)

    with pytest.raises(RuntimeError, match='upload failed'):
        project.publish()

    assert not git_pushed
    assert not (in_tmp_path / RELEASE_STATE_FILENAME).exists()


def test_publish_retries_pending_git_push(in_tmp_path, get_appmaker, monkeypatch):
    get_appmaker()
    project = Project()
    pending_path = in_tmp_path / RELEASE_STATE_FILENAME
    calls = []

    monkeypatch.setattr(
        'makeapp.apptools.DistHelper.upload',
        lambda: calls.append('upload'),
    )

    def fail_push():
        calls.append('push')
        raise RuntimeError('push failed')

    monkeypatch.setattr(project.vcs, 'push', fail_push)

    with pytest.raises(RuntimeError, match='push failed'):
        project.publish()

    assert calls == ['upload', 'push']
    assert pending_path.read_text() == '{"step": "git-push"}\n'

    monkeypatch.setattr(project.vcs, 'push', lambda: calls.append('retry push'))
    project.publish()

    assert calls == ['upload', 'push', 'retry push']
    assert not pending_path.exists()


def test_venv(in_tmp_path, get_appmaker, assert_content):

    get_appmaker()

    vcs = VcsHelper.get()
    vcs.commit('initial')

    project = Project()

    project.venv_init()
    assert_content(in_tmp_path / '.venv/pyvenv.cfg', [
        'version_info ='
    ])

    project.venv_init(reset=True)
    assert_content(in_tmp_path / '.venv/pyvenv.cfg', [
        'version_info ='
    ])


def test_changelog(in_tmp_path):

    fchangelog = (in_tmp_path / ChangelogData.filename)
    fchangelog.write_text(dedent("""    # {{ app_name }} changelog

    ### Unreleased
    * ++ Basic functionality.

    """))

    def load():
        data_ = ChangelogData.get()
        contents_ = data_.file_helper.contents
        return data_, contents_

    data, contents = load()
    assert len(contents) == 5

    assert data.deduce_version_increment() == 'minor'
    data.sort_version_changes()

    data.add_change('Some fix')
    assert len(contents) == 6

    assert data.get_version_summary() == '* ** Some fix\n* ++ Basic functionality.'

    assert data.version_bump((1, 2, 3)) == 'v1.2.3'
    assert '1.2.3' in contents[2]
    data.write()
    changelog_bytes = fchangelog.read_bytes()
    assert changelog_bytes.endswith(b'\n')
    assert not changelog_bytes.endswith(b'\n\n')

    # another loop
    data, contents = load()
    assert len(contents) == 7  # Unreleased added
    assert data.deduce_version_increment() == 'patch'

    data.add_change('+ Some feature')
    assert len(contents) == 8
    assert data.deduce_version_increment() == 'minor'

    assert data.get_version_summary() == '* ++ Some feature'


def test_project_path_is_used_for_settings_and_commands(tmp_path, monkeypatch):
    project_path = tmp_path / 'target'
    project_path.mkdir()
    (project_path / 'pyproject.toml').write_text(
        '[tool.makeapp]\nmarker = "target"\n'
    )
    project = Project(project_path=project_path)
    command_paths = []

    def record_path(*args, **kwargs):
        command_paths.append(Path.cwd())
        return {
            'OK': [],
            'FAIL': [],
        }

    monkeypatch.setattr('makeapp.apptools.TestsHelper.run_tests', record_path)
    monkeypatch.setattr('makeapp.apptools.Ruff.check', record_path)
    monkeypatch.setattr('makeapp.apptools.MkDocs.build', record_path)
    monkeypatch.setattr(project.venv, 'initialize', record_path)

    assert project.get_settings() == {'marker': 'target'}
    project.run_tests()
    project.style()
    project.docs(serve=False)
    project.venv_init()

    assert command_paths == [project_path] * 4


def test_release_package_prefers_normalized_project_name(tmp_path):
    first = tmp_path / 'src' / 'first'
    preferred = tmp_path / 'src' / 'sample_package'
    first.mkdir(parents=True)
    preferred.mkdir()
    (first / '__init__.py').touch()
    (preferred / '__init__.py').touch()

    assert Project.find_release_package(tmp_path, 'sample-package') == preferred


def test_release_package_rejects_ambiguous_candidates(tmp_path):
    for name in ('first', 'second'):
        package = tmp_path / 'src' / name
        package.mkdir(parents=True, exist_ok=True)
        (package / '__init__.py').touch()

    with pytest.raises(ProjectorExeption, match='Unable to identify release package'):
        Project.find_release_package(tmp_path, 'unknown')


def test_project_reports_missing_vcs(tmp_path):
    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "sample"\n')
    project = Project(project_path=tmp_path)

    with pytest.raises(ProjectorExeption, match='No supported VCS repository'):
        project.pull()


def test_changelog_finds_headings_after_preamble(in_tmp_path):
    fchangelog = in_tmp_path / ChangelogData.filename
    fchangelog.write_text(dedent('''
        # Sample changelog

        Project release history.

        ```md
        ### Unreleased
        ```

        ### v1.0.0 [2026-01-01]
        * ** Existing change.
    ''').lstrip())

    data = ChangelogData.get()
    line_idx = data.file_helper.line_idx

    assert data.file_helper.contents[line_idx] == '### Unreleased'
    assert data.file_helper.contents[line_idx + 2].startswith('### v1.0.0')
