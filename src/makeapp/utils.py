import fileinput
import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from subprocess import Popen, PIPE, STDOUT
from typing import Generator, List, Optional, Dict

from .exceptions import CommandError

LOG = logging.getLogger(__name__)
PYTHON_VERSION = sys.version_info


def configure_logging(
        level: Optional[int] = None,
        logger: Optional[logging.Logger] = None,
        format: str = '%(message)s'
):
    """Switches on logging at a given level. For a given logger or globally.

    :param level:
    :param logger:
    :param format:

    """
    logging.basicConfig(format=format, level=level if logger else None)
    logger and logger.setLevel(level or logging.INFO)


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


def replace_infile(filepath: str, pairs: Dict[str, str]):
    """Replaces some term by another in file contents.

    :param filepath:
    :param pairs: search -> replace.

    """
    with fileinput.input(files=filepath, inplace=True) as f:

        for line in f:

            for search, replace in pairs.items():
                line = line.replace(search, replace)

            sys.stdout.write(line)


def check_command(command: str, hint: str):
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


def run_command(command: str, *, err_msg: str = '') -> List[str]:
    """Runs a command in a shell process.

    Returns a list of strings gathered from a command.

    :param command:

    :param err_msg: Message to show on error.

    :raises: CommandError

    """
    prc = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)

    LOG.debug(f'Run command: `{command}` ...')

    data = []

    out, _ = prc.communicate()

    if isinstance(out, bytes):
        out = out.decode('utf-8')

    has_error = prc.returncode

    for item in out.splitlines():
        item = item.strip()

        if not item:
            continue

        data.append(item)

    if has_error:
        raise CommandError(err_msg or f"Command `{command}` failed: %s" % '\n'.join(data))

    return data
