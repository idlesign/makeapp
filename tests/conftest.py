import os
from pathlib import Path

import pytest

os.environ['UV_NO_DEV'] = '1'  # disable dev packages in venv to speedup tests

@pytest.fixture
def get_appmaker():

    def get_appmaker_(
            app_name: str = 'dummy',
            *,
            templates: list[str] = None,
            rollout: bool = True,
            init_venv: bool = False
    ):

        from makeapp.appmaker import AppMaker

        app_maker = AppMaker(app_name, templates_to_use=templates)

        app_maker.update_settings_complex(
            # config=configuration_file,
            dictionary={
                'description': 'testdummydescr',
                'author': 'The Librarian',
                'author_email': 'librarian@discworld.wrld',
                'url': 'https://discworld.wrld/librarian/{{ app_name }}',
            },
        )

        if rollout:

            app_maker.rollout(
                '.',
                overwrite=True,
                init_repository=True,
                init_venv=init_venv,
                remote_address='some@some.com',
                remote_push=False,
            )

        return app_maker

    return get_appmaker_


@pytest.fixture
def assert_content():

    def assert_content_(fpath: Path, lines):

        contents = fpath.read_text()
        for line in lines:
            assert line in contents

    return assert_content_


@pytest.fixture
def assert_cleanup():

    def assert_cleanup_(fpath):
        assert not fpath.exists()

    return assert_cleanup_


@pytest.fixture
def in_tmp_path(tmp_path):
    before = os.getcwd()
    try:
        os.chdir(tmp_path)
        yield tmp_path
    finally:
        os.chdir(before)
