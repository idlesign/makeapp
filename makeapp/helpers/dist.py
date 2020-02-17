from ..utils import run_command


class DistHelper:
    """Encapsulates Python distribution related logic."""

    @classmethod
    def run_command(cls, command):
        """Basic command runner."""
        return run_command(f'python setup.py {command}')

    @classmethod
    def upload(cls):
        """Builds a package and uploads it to PyPI."""
        cls.run_command('clean --all sdist bdist_wheel upload')
