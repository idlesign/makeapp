from textwrap import dedent

from makeapp.helpers.vcs import VcsHelper
from makeapp.apptools import Project


def test_git(tmpdir, get_appmaker, assert_content):

    with tmpdir.as_cwd():

        get_appmaker()

        vcs = VcsHelper.get()
        vcs.commit('initial')

        project = Project()
        project.add_change(['fix1', '* change', '! warn', '+ add'])

        assert_content(tmpdir, 'CHANGELOG', [
            dedent('''
            ! warn.
            + add.
            + Basic functionality.
            * change.
            * fix1.
            ''')
        ])

        version, summary = project.get_release_info()

        assert version == 'v0.1.0'
        assert summary == '! warn.\n+ add.\n+ Basic functionality.\n* change.\n* fix1.'

        project.release(version, summary)
