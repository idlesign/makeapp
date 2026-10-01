
import pytest
import requests

from makeapp.appmaker import AppMaker
from makeapp.exceptions import AppMakerException


def test_default(in_tmp_path, get_appmaker, assert_content):

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
        '__pycache__',
    ])

    assert_content(in_tmp_path / 'CHANGELOG.md', [
        '## Unreleased\n',
    ])

    assert_content(in_tmp_path / 'pyproject.toml', [
        'name = "The Librarian"',
        'email = "librarian@discworld.wrld"',
    ])

    assert_content(in_tmp_path / 'docs/index.md', [
        '*testdummydescr*',
        'uv add dummy',
    ])

    assert_content(in_tmp_path / 'pyproject.toml', [
        '{include-group = "docs"}',
        '"mkdocs-material"',
    ])

    assert_content(in_tmp_path / '.venv/pyvenv.cfg', [
        'version_info ='
    ])

    assert_content(in_tmp_path / 'tests/test_basic.py', [
        'import pytest',
        "pytest.raises(ValueError, match='Tested!')",
    ])

    readme = (in_tmp_path / 'README.md').read_bytes()
    assert readme.endswith(b'\n')
    assert not readme.endswith(b'\n\n')


def test_tpl_userdefined(in_tmp_path, tmp_path, get_appmaker, assert_content):

    with open(tmp_path / 'pyproject.toml', 'w') as f:
        f.write('{% extends parent_template %}\n'
            "{% block entry_points_custom %}{{ super() }}# some custom{% endblock %}")

    get_appmaker(templates=[f'{tmp_path}'])

    assert_content(in_tmp_path / 'pyproject.toml', [
        '# some custom',
    ])


def test_webscaff_uses_integrated_pytest_support(monkeypatch):
    monkeypatch.setattr('makeapp.appconfig.sleep', lambda _: None)

    app_maker = AppMaker('dummy', templates_to_use=['webscaff'])

    assert [template.name for template in app_maker.app_templates] == [
        '__default__',
        'webscaff',
    ]


def test_invalid_package_name_is_rejected():
    with pytest.raises(AppMakerException, match='Invalid Python package name'):
        AppMaker('../../outside')


def test_template_target_must_stay_within_destination(tmp_path, monkeypatch):
    app_maker = AppMaker('dummy')
    monkeypatch.setattr(app_maker, '_get_template_files', lambda: {'../outside': object()})

    with pytest.raises(AppMakerException, match='escapes destination'):
        app_maker.rollout(tmp_path / 'target')

    assert not (tmp_path / 'outside').exists()


def test_app_name_availability_uses_timeout(get_appmaker, monkeypatch):
    calls = []

    def get(url, *, timeout):
        calls.append((url, timeout))
        status_code = 200 if url.endswith('/django/') else 404
        return type('Response', (), {'status_code': status_code})()

    monkeypatch.setattr('makeapp.appmaker.requests.get', get)

    assert not get_appmaker('django', rollout=False).check_app_name_is_available()
    assert get_appmaker('available', rollout=False).check_app_name_is_available()
    assert calls == [
        ('https://pypi.org/simple/django/', 5),
        ('https://pypi.org/simple/available/', 5),
    ]


@pytest.mark.parametrize('status_code', [403, 429, 500])
def test_app_name_availability_rejects_unknown_status(
        status_code, get_appmaker, monkeypatch
):
    response = type('Response', (), {'status_code': status_code})()
    monkeypatch.setattr(
        'makeapp.appmaker.requests.get',
        lambda *args, **kwargs: response,
    )

    with pytest.raises(AppMakerException, match=f'HTTP {status_code}'):
        get_appmaker('dummy', rollout=False).check_app_name_is_available()


def test_app_name_availability_handles_network_error(get_appmaker, monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout('timed out')

    monkeypatch.setattr('makeapp.appmaker.requests.get', fail)

    with pytest.raises(AppMakerException, match='Unable to check application name'):
        get_appmaker('dummy', rollout=False).check_app_name_is_available()
