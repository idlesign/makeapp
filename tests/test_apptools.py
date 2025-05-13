from textwrap import dedent

from makeapp.helpers.vcs import VcsHelper
from makeapp.apptools import Project


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
    assert summary == (
        '* ++ add.\n'
        '* ++ Basic functionality.\n'
        '* ** change.\n'
        '* ** fix1.\n'
        '* ++ Basic functionality.'
    )

    project.release(version, summary)

    issued_commands = []

    def dummy_communicate(self, *args, **kwargs):
        issued_commands.append(self.args)
        return b'', b''

    monkeypatch.setattr('makeapp.utils.Popen.communicate', dummy_communicate)
    project.publish()

    assert issued_commands == [
        'git push',
        'git push --tags',
        'uv build',
        'uv publish'
    ]


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
