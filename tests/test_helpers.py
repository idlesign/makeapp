from makeapp.helpers.dist import DistHelper
from makeapp.helpers.tests import TestsHelper


def test_disthelper():
    assert DistHelper


class TestTestsHelper:

    def test_get_matrix_github(self, datafix_dir):
        assert TestsHelper.get_matrix_github(datafix_dir / 'github_matrix.yml') == [
            {'django-version': 2.0, 'python-version': '3.10'},
            {'django-version': 3.0, 'python-version': '3.10'},
            {'django-version': 4.0, 'python-version': '3.10'},
            {'django-version': 5.0, 'python-version': '3.10'},
            {'django-version': 2.0, 'python-version': 3.11},
            {'django-version': 3.0, 'python-version': 3.11},
            {'django-version': 4.0, 'python-version': 3.11},
            {'django-version': 5.0, 'python-version': 3.11},
            {'django-version': 3.0, 'python-version': 3.12},
            {'django-version': 4.0, 'python-version': 3.12},
            {'django-version': 5.0, 'python-version': 3.12},
            {'django-version': 6.0, 'python-version': 3.12},
            {'django-version': 5.0, 'python-version': 3.14},
            {'django-version': 6.0, 'python-version': 3.14}
        ]

    def test_apply_context(self):
        apply = TestsHelper.apply_context
        assert apply(
            'a${{django-version}}b && |${{ python }}|',
            {'django-version': 2.0, 'python': '3.10'}
        ) == 'a2.0b && |3.10|'
