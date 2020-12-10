from makeapp.helpers.dist import DistHelper


def test_disthelper():
    assert DistHelper.python_bin == 'python'
