from ..utils import run_command, check_command, PYTHON_VERSION


class DistHelper:
    """Encapsulates Python distribution related logic."""

    python_bin: str = 'python' if PYTHON_VERSION[0] == 3 else 'python3'
    """Name of python binary that'll be used for commands run."""

    check_command(python_bin, 'Python 3+')

    run_command(
        f'{python_bin} -m wheel version',
        err_msg=f"Please install 'wheel' module to proceed: {python_bin} -m pip install wheel")

    @classmethod
    def run_command(cls, command):
        """Basic command runner."""
        return run_command(f'{cls.python_bin} setup.py {command}')

    @classmethod
    def upload(cls):
        """Builds a package and uploads it to PyPI."""
        cls.run_command('clean --all sdist bdist_wheel upload')
