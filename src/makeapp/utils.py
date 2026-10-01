import configparser
import fileinput
import logging
import os
import shlex
import shutil
import sys
import tempfile
from collections.abc import Generator, Sequence
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
    if shutil.which(command) is None:
        raise CommandError(
            f"Failed to execute '{command}' command. "
            f"Check {hint} is installed and available.")


def run_command(
        command: str | Sequence[str | os.PathLike],
        *,
        err_msg: str = '',
        env: dict | None = None,
        capture: bool = True,
) -> list[str]:
    """Run a command without invoking a shell.

    Returns stripped, non-empty output lines. String commands are split with
    :func:`shlex.split` for backward compatibility; argument lists are preferred.

    :param command: Command arguments.
    :param err_msg: Message to show on error.
    :param env: Environment variables to use.
    :param capture: Capture stdout and stderr and return as lines.

    :raises: CommandError

    """
    if isinstance(command, str):
        command = shlex.split(command)

    args = [os.fspath(item) for item in command]
    command_display = shlex.join(args)

    if env:
        env = {**os.environ, **env}

    LOG.debug(f'Run command: {command_display} ...')
    kwargs = {}

    if capture:
        kwargs = {'stdout': PIPE, 'stderr': STDOUT}

    prc = Popen(args, shell=False, universal_newlines=True, env=env, **kwargs)
    out, _ = prc.communicate()

    if out:
        LOG.debug(indent(out, prefix="    "))
        data = [stripped for item in out.splitlines() if (stripped := item.strip())]

    else:
        data = []

    if prc.returncode:
        raise CommandError(err_msg or f"Command `{command_display}` failed: %s" % '\n'.join(data))

    return data


class Ruff:
    """Ruff wrapper."""

    @classmethod
    def _run(cls, args: Sequence[str]) -> list[str]:
        return run_command(['ruff', *args], capture=False)

    @classmethod
    def check(cls, *, fix: bool = True) -> list[str]:
        return cls._run(['check', *(['--fix'] if fix else [])])


class MkDocs:
    """MkDocs wrapper."""

    @classmethod
    def _run(cls, args: Sequence[str]) -> list[str]:
        return run_command(['mkdocs', *args], capture=False)

    @classmethod
    def serve(cls) -> list[str]:
        return cls._run(['serve', '-o'])

    @classmethod
    def build(cls) -> list[str]:
        return cls._run(['build'])


class Uv:
    """Uv wrapper."""

    @classmethod
    def exec(cls, command: str | Sequence[str], env: dict | None = None) -> list[str]:
        if isinstance(command, str):
            command = shlex.split(command)
        return run_command(['uv', *command], env=env, capture=False)

    @classmethod
    def upgrade(cls) -> list[str]:
        return cls.exec(['self', 'update'])

    @classmethod
    def tool_install(cls, name: str) -> list[str]:
        return cls.exec(['tool', 'install', name])

    @classmethod
    def tool_upgrade(cls, name: str) -> list[str]:
        return cls.exec(['tool', 'upgrade', name, '--reinstall'])

    @classmethod
    def sync(cls) -> list[str]:
        return cls.exec(['sync'])

    @classmethod
    def install(cls):
        if sys.platform == 'win32':
            return run_command([
                'powershell',
                '-ExecutionPolicy',
                'ByPass',
                '-c',
                'irm https://astral.sh/uv/install.ps1 | iex',
            ], capture=False)

        with tempfile.NamedTemporaryFile() as script:
            run_command([
                'curl',
                '-LsSf',
                'https://astral.sh/uv/install.sh',
                '-o',
                script.name,
            ], capture=False)
            return run_command(['sh', script.name], capture=False)
