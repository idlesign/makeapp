import io
import logging
from typing import List, Union

LOG = logging.getLogger(__name__)


class FileHelper:
    """Encapsulates file related functions."""

    def __init__(self, filepath, line_idx, contents):
        self.filepath = filepath
        self.line_idx = line_idx
        self.contents = contents

    @classmethod
    def read_file(cls, fpath: str) -> List[str]:
        """Reads a file from FS. Returns a lis of strings from it.

        :param fpath: File path

        """
        with io.open(fpath, encoding='utf-8') as f:
            data = f.read().splitlines()

        return data

    def write(self):
        """Writes updated contents back to a file."""

        LOG.debug(f'Writing `{self.filepath}` ...')

        with io.open(self.filepath, 'w', encoding='utf-8') as f:
            f.write('\n'.join(self.contents))

    def line_replace(self, value: str, offset: int = 0):
        """Replaces a line in file.

        :param value: New line.
        :param offset: Offset from line_idx

        """
        target_idx = self.line_idx + offset
        self.contents[target_idx] = value

    def insert(self, value: Union[List[str], str], offset: int = 1):
        """Inserts a line (or many) into file.

        :param value: New line(s).
        :param offset: Offset from line_idx

        """
        target_idx = self.line_idx + offset

        if not isinstance(value, list):
            value = [value]

        self.contents[target_idx:target_idx] = value

    def iter_after(self, offset: int) -> str:
        """Generator. Yields lines after line_idx

        :param offset:

        """
        target_idx = self.line_idx + offset

        for line in self.contents[target_idx:]:
            yield line
