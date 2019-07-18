import fileinput
import logging
import os
import shutil
import sys
import tempfile
from contextlib import contextmanager
from subprocess import Popen, PIPE, STDOUT

from jinja2 import _compat

from .exceptions import CommandError

LOG = logging.getLogger(__name__)
PYTHON_VERSION = sys.version_info
PY2 = _compat.PY2


def configure_logging(level=None, logger=None, format='%(message)s'):
    """Switches on logging at a given level. For a given logger or globally.

    :param int level:
    :param logger:
    :param str|unicode format:

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
def temp_dir():
    """Context manager to temporarily create a directory.

    :rtype: str

    """
    dir_tmp = tempfile.mkdtemp(prefix='makeapp_')

    try:
        yield dir_tmp

    finally:
        shutil.rmtree(dir_tmp, ignore_errors=True)


def replace_infile(filepath, pairs):
    """Replaces some term by another in file contents.

    :param str filepath:
    :param tuple[tuple[str, str]] pairs: (search, replace) tuples.

    """
    with fileinput.input(files=filepath, inplace=True) as f:
        for line in f:
            for (search, replace) in pairs:
                line = line.replace(search, replace)
            sys.stdout.write(line)


def check_command(command, hint):
    """Checks whether a command is available.
    If not - raises an exception.

    :param str command:
    :param str hint:

    """
    try:
        run_command('type %s' % command)

    except CommandError:
        raise CommandError(
            "Unable to find '%s' command. Check %s is installed and available." % (command, hint))


def run_command(command):
    """Runs a command in a shell process.

    Returns a list of strings gathered from a command.

    :param str|unicode command:
    :raises: CommandError
    :rtype: list
    """
    prc = Popen(command, stdout=PIPE, stderr=STDOUT, shell=True, universal_newlines=True)

    LOG.debug('Run command: `%s` ...', command)
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
        raise CommandError('Command `%s` failed: %s' % (command, '\n'.join(data).encode('utf8')))

    return data
