import logging
from pathlib import Path
from shutil import rmtree

from ..utils import run_command

LOG = logging.getLogger(__name__)


class VenvHelper:
    """Encapsulates virtual environment related functions."""

    dirname = '.venv'

    def __init__(self, project_path: str):
        self.venv_path = Path(project_path) / self.dirname

    def initialize(self, *, reset: bool = False):
        LOG.info(f'Initializing virtual environment [{reset=}] ...')

        if reset:
            self.remove()

        run_command('uv sync')

    def remove(self):
        path = self.venv_path
        LOG.info(f'Removing {path} ...')
        rmtree(f'{path}', ignore_errors=True)

    def register_tool(self):
        LOG.info(f'Registering application CLI as a tool ...')
        run_command('uv tool install --force -e .')
