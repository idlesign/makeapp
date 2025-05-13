import pytest


class TestApp:

    def test_method(self):

        assert 1 == 1

        with pytest.raises(Exception):
            raise Exception('Tested!')
