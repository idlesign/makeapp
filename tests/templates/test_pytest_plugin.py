
def test_tpl_pytestplugin(in_tmp_path, get_appmaker, assert_content):

    get_appmaker(templates=['pytestplugin'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        'pytest11',
        'dummy = "dummy.entry"',
        '"Framework :: Pytest"',
    ])

    assert_content(in_tmp_path / 'src/dummy/entry.py', [
        "return 'itworks'",
    ])


    assert_content(in_tmp_path / 'tests/test_basic.py', [
        "rename_me == 'itworks'",
    ])
