from textwrap import dedent

from makeapp.apptools import Project, ChangelogData
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

    # another loop
    data, contents = load()
    assert len(contents) == 7  # Unreleased added
    assert data.deduce_version_increment() == 'patch'

    data.add_change('+ Some feature')
    assert len(contents) == 8
    assert data.deduce_version_increment() == 'minor'

    assert data.get_version_summary() == '* ++ Some feature'
