
def test_tpl_console(in_tmp_path, get_appmaker, assert_content):
    get_appmaker(templates=['console'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        'dummy = "dummy.cli:main"',
    ])
