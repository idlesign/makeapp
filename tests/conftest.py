import pytest


@pytest.fixture
def get_appmaker():

    def get_appmaker_(app_name='dummy', templates=None, *, rollout=True):

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
                remote_address='some@some.com',
                remote_push=False,
            )

        return app_maker

    return get_appmaker_


@pytest.fixture
def assert_content():

    def assert_content_(tmpdir, filename, lines):

        contents = tmpdir.join(filename).read()
        for line in lines:
            assert line in contents

    return assert_content_


@pytest.fixture
def assert_cleanup():

    def assert_cleanup_(tmpdir, filename):
        assert not tmpdir.join(filename).exists()

    return assert_cleanup_
