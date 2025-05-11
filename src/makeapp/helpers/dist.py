from shutil import rmtree

from ..utils import run_command, check_command


class DistHelper:
    """Encapsulates Python distribution related logic."""

    python_bin: str = 'python3'
    """Name of python binary that'll be used for commands run."""

    check_command(python_bin, 'Python 3+')

    @classmethod
    def ensure(cls):
        """Ensures dist helper is functional."""
        run_command(
            f'{cls.python_bin} -m wheel version',
            err_msg=f"Please install 'wheel' module to proceed: {cls.python_bin} -m pip install wheel")

    @classmethod
    def run_command(cls, command):
        """Basic command runner."""
        return run_command(f'{cls.python_bin} setup.py {command}')

    @classmethod
    def upload(cls):
        """Builds a package and uploads it to PyPI."""

        rmtree('dist/', ignore_errors=True)  # cleanup

        cls.run_command('clean --all sdist bdist_wheel')

        # setuptools 'upload' essentially has become broken
        # https://github.com/python/cpython/issues/89753
        # https://github.com/pypa/distutils/issues/25
        # using twine instead
        run_command('twine upload dist/*')
