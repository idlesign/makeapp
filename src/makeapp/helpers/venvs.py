import logging
import re
from pathlib import Path
from shutil import rmtree

from ..utils import Uv, run_command

LOG = logging.getLogger(__name__)


class VenvHelper:
    """Encapsulates virtual environment related functions."""

    dirname = '.venv'

    def __init__(self, project_path: str):
        self.venv_path = Path(project_path) / self.dirname

    @staticmethod
    def read_python_version(venv_path: Path) -> tuple[int, int] | None:
        """Returns the Python version of the given virtual environment as (major, minor).

        :param venv_path: Virtual environment directory path.

        """
        python_bin = None

        for bin_dir in ('bin', 'Scripts'):
            candidate = venv_path / bin_dir / 'python'

            if candidate.exists():
                python_bin = candidate
                break

        if python_bin is None:
            return None

        output = run_command([python_bin, '--version'])

        if not output:
            return None

        match = re.search(r'(\d+)\.(\d+)', output[0])
        return (int(match.group(1)), int(match.group(2))) if match else None

    def get_python_version(self) -> tuple[int, int] | None:
        """Returns the virtual environment Python version as (major, minor)."""
        return self.read_python_version(self.venv_path)

    def initialize(self, *, reset: bool = False):
        LOG.info(f'Initializing virtual environment [{reset=}] ...')

        if reset:
            self.remove()

        Uv.sync()

    def remove(self):
        path = self.venv_path
        LOG.info(f'Removing {path} ...')
        rmtree(f'{path}', ignore_errors=True)

    def register_tool(self):
        LOG.info('Registering application CLI as a tool ...')
        Uv.tool_install('.', force=True, editable=True)
