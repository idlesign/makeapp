import io
import logging


LOG = logging.getLogger(__name__)


class FileHelper(object):
    """Encapsulates file related functions."""

    def __init__(self, filepath, line_idx, contents):
        self.filepath = filepath
        self.line_idx = line_idx
        self.contents = contents

    @classmethod
    def read_file(cls, fpath):
        """Reads a file from FS. Returns a lis of strings from it.

        :param str|unicode fpath: File path
        :rtype: list
        """
        with io.open(fpath, encoding='utf-8') as f:
            data = f.read().splitlines()
        return data

    def write(self):
        """Writes updated contents back to a file."""
        LOG.debug('Writing `%s` ...', self.filepath)
        with io.open(self.filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.contents))

    def line_replace(self, value, offset=0):
        """Replaces a line in file.

        :param str|unicode value: New line.
        :param int offset: Offset from line_idx
        """
        target_idx = self.line_idx + offset
        self.contents[target_idx] = value

    def insert(self, value, offset=1):
        """Inserts a line (or many) into file.

        :param str|unicode|list value: New line(s).
        :param int offset: Offset from line_idx
        """
        target_idx = self.line_idx + offset
        if not isinstance(value, list):
            value = [value]
        self.contents[target_idx:target_idx] = value

    def iter_after(self, offset):
        """Generator. Yields lines after line_idx

        :param offset:
        :rtype: str|unicode
        """
        target_idx = self.line_idx + offset
        for line in self.contents[target_idx:]:
            yield line
