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
        path = self.venv_path

        if reset:
            LOG.debug(f'Remove {path} ...')
            rmtree(f'{path}', ignore_errors=True)

        run_command('uv sync')
