import configparser
import fileinput
import logging
import os
import shutil
import sys
import tempfile
from collections.abc import Generator
from configparser import ConfigParser
from contextlib import contextmanager
from pathlib import Path
from subprocess import PIPE, STDOUT, Popen
from textwrap import indent

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


def run_command(command: str, *, err_msg: str = '', env: dict | None = None, capture: bool = True) -> list[str]:
    """Runs a command in a shell process.

    Returns a list of strings gathered from a command.

    :param command:
    :param err_msg: Message to show on error.
    :param env: Environment variables to use.
    :param capture: Capture stdout and stderr and return as lines.

    :raises: CommandError

    """
    if env:
        env = {**os.environ, **env}

    LOG.debug(f'Run command: {command} ...')
    kwargs = {}

    if capture:
        kwargs = {'stdout': PIPE, 'stderr': STDOUT}

    prc = Popen(command, shell=True, universal_newlines=True, env=env, **kwargs)
    out, _ = prc.communicate()

    if out:
        LOG.debug(indent(out, prefix="    "))
        data = [stripped for item in out.splitlines() if (stripped := item.strip())]

    else:
        data = []

    if prc.returncode:
        raise CommandError(err_msg or f"Command `{command}` failed: %s" % '\n'.join(data))

    return data


class Ruff:
    """Ruff wrapper."""

    @classmethod
    def _run(cls, cmd: str) -> list[str]:
        return run_command(f'ruff {cmd}', capture=False)

    @classmethod
    def check(cls, fix: bool = True) -> list[str]:
        return cls._run(f'check{" --fix" if fix else ""}')


class MkDocs:
    """MkDocs wrapper."""

    @classmethod
    def _run(cls, cmd: str) -> list[str]:
        return run_command(f'mkdocs {cmd}', capture=False)

    @classmethod
    def serve(cls) -> list[str]:
        return cls._run('serve -o')

    @classmethod
    def build(cls) -> list[str]:
        return cls._run('build')


class Uv:
    """Uv wrapper."""

    @classmethod
    def _run(cls, cmd: str) -> list[str]:
        return run_command(f'uv {cmd}', capture=False)

    @classmethod
    def upgrade(cls) -> list[str]:
        return cls._run('self update')

    @classmethod
    def tool_install(cls, name: str) -> list[str]:
        return cls._run(f'tool install {name}')

    @classmethod
    def tool_upgrade(cls, name: str) -> list[str]:
        return cls._run(f'tool upgrade {name} --reinstall')

    @classmethod
    def sync(cls) -> list[str]:
        return cls._run('sync')

    @classmethod
    def install(cls):
        return run_command('curl -LsSf https://astral.sh/uv/install.sh | sh', capture=False)
