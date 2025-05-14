
def test_tpl_click(in_tmp_path, get_appmaker, assert_content):

    get_appmaker(templates=['click'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        '"click"',
        'dummy = "dummy.cli:main"',
    ])
