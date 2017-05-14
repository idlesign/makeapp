import os
import logging
from contextlib import contextmanager
from subprocess import Popen, PIPE

from .exceptions import CommandError


LOG = logging.getLogger(__name__)


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
    prc = Popen(command, stdout=PIPE, shell=True, universal_newlines=True)

    LOG.debug('Run command: `%s` ...', command)
    data = []

    result = ''.join(item.decode('utf-8') for item in prc.communicate() if item)
    has_error = prc.returncode

    for item in result.splitlines():
        if not item:
            continue

        item = item.strip()

        if not item:
            continue

        data.append(item)

    if has_error:
        raise CommandError('Command `%s` failed: %s' % (command, data))

    return data
