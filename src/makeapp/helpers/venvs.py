import logging
import re
from pathlib import Path
from shutil import rmtree

from ..utils import Uv

LOG = logging.getLogger(__name__)


class VenvHelper:
    """Encapsulates virtual environment related functions."""

    dirname = '.venv'

    def __init__(self, project_path: str):
        self.venv_path = Path(project_path) / self.dirname

    def get_python_version(self) -> tuple[int, int] | None:
        """Returns the virtual environment Python version as (major, minor)."""
        if not self.venv_path.exists():
            return None

        output = Uv.exec([
            'run', '--project', str(self.venv_path.parent), '--no-sync', 'python', '--version'])

        if not output:
            return None

        match = re.search(r'(\d+)\.(\d+)', output[0])
        return (int(match.group(1)), int(match.group(2))) if match else None

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
