import configparser
import fileinput
import logging
import os
import shutil
import sys
import tempfile
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from subprocess import Popen, PIPE, STDOUT
from typing import Generator

from .exceptions import CommandError

LOG = logging.getLogger(__name__)
PYTHON_VERSION = sys.version_info


def configure_logging(
        level: int | None = None,
        logger: logging.Logger | None = None,
        format: str = '%(message)s'
):
    """Switches on logging at a given level. For a given logger or globally.

    :param level:
    :param logger:
    :param format:

    """
    logging.basicConfig(format=format, level=level if level else None)
    logger and logger.setLevel(level or logging.INFO)


def get_user_dir() -> Path:
    """Returns the user's home directory."""
    return Path(os.path.expanduser('~'))


def read_ini(fpath: Path) -> ConfigParser:
    """Read a .ini file.

    :param fpath:
    """
    cfg = configparser.ConfigParser()
    cfg.read(f'{fpath}')
    return cfg


@contextmanager
def chdir(target_path):
    """Context manager.
     
    Temporarily switches the current working directory.
    
    """
    curr_dir = os.getcwd()
    os.chdir(target_path)

    try:
        yield

    finally:
        os.chdir(curr_dir)


@contextmanager
def temp_dir() -> Generator[str, None, None]:
    """Context manager to temporarily create a directory."""

    dir_tmp = tempfile.mkdtemp(prefix='makeapp_')

    try:
        yield dir_tmp

    finally:
        shutil.rmtree(dir_tmp, ignore_errors=True)


def replace_infile(filepath: str, pairs: dict[str, str]):
    """Replaces some term by another in file contents.

    :param filepath:
    :param pairs: search -> replace.

    """
    with fileinput.input(files=filepath, inplace=True) as f:

        for line in f:

            for search, replace in pairs.items():
                line = line.replace(search, replace)

            sys.stdout.write(line)


def check_command(command: str, *, hint: str):
    """Checks whether a command is available.
    If not - raises an exception.

    :param command:
    :param hint:

    """
    try:
        run_command(f'type {command}')

    except CommandError:
        raise CommandError(
            f"Failed to execute '{command}' command. "
            f"Check {hint} is installed and available.")


def run_command(command: str, *, err_msg: str = '', env: dict | None = None) -> list[str]:
    """Runs a command in a shell process.

    Returns a list of strings gathered from a command.

    :param command:

    :param err_msg: Message to show on error.

    :param env: Environment variables to use.

    :raises: CommandError

    """
    if env:
        env = {**os.environ, **env}

    LOG.debug(f'Run command: `{command}` ...')

    prc = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True, env=env)

    data = []
    out, _ = prc.communicate()

    LOG.debug(f'Command output:\n`{out}`')

    for item in out.splitlines():
        item = item.strip()

        if not item:
            continue

        data.append(item)

    if prc.returncode:
        raise CommandError(err_msg or f"Command '{command}' failed: {'\n'.join(data)}")

    return data
