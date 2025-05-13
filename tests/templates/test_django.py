
def test_tpl_django(in_tmp_path, get_appmaker, assert_content, assert_cleanup):

    get_appmaker(templates=['django'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        'pytest-djangoapp>=',
    ])

    assert_content(in_tmp_path / 'src/dummy/apps.py', [
        "name = 'dummy'",
        "verbose_name = _('Dummy')",
    ])

    assert_cleanup(in_tmp_path / 'tests')
