import os
import logging
from contextlib import contextmanager
from subprocess import Popen, PIPE, STDOUT

from .exceptions import CommandError


LOG = logging.getLogger(__name__)


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
