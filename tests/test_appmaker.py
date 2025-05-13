
def test_default(in_tmp_path, get_appmaker, assert_content):

    assert not get_appmaker('django', rollout=False).check_app_name_is_available()
    assert get_appmaker('x7t8whatsthat', rollout=False).check_app_name_is_available()

    app_maker = get_appmaker(init_venv=True)

    settings_str = app_maker.get_settings_string()

    assert 'app_name: dummy' in settings_str
    assert 'Chosen VCS: Git' in settings_str
    assert 'vcs: git'

    assert_content(in_tmp_path / 'README.md', [
        '# dummy\n',
        '*testdummydescr*',
        'https://discworld.wrld/librarian/dummy',
    ])

    assert_content(in_tmp_path / '.gitignore', [
        'docs/_build/',
    ])

    assert_content(in_tmp_path / 'CHANGELOG.md', [
        '## Unreleased\n',
    ])

    assert_content(in_tmp_path / 'pyproject.toml', [
        'name = "The Librarian"',
        'email = "librarian@discworld.wrld"',
    ])

    assert_content(in_tmp_path / 'docs/source/conf.py', [
        'from dummy import VERSION_STR',
    ])

    assert_content(in_tmp_path / '.venv/pyvenv.cfg', [
        'version_info ='
    ])

    assert_content(in_tmp_path / 'tests/test_basic.py', [
        'import pytest',
    ])


def test_tpl_userdefined(in_tmp_path, tmp_path, get_appmaker, assert_content):

    with open(tmp_path / 'pyproject.toml', 'w') as f:
        f.write('{% extends parent_template %}\n'
            "{% block entry_points_custom %}{{ super() }}# some custom{% endblock %}")

    get_appmaker(templates=[f'{tmp_path}'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        '# some custom',
    ])
