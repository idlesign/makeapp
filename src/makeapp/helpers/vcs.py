import os
import shlex
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from ..exceptions import CommandError, ProjectorExeption
from ..utils import run_command


class VcsHelper:
    """Base helper for VCS related actions."""

    title = None
    alias = None
    branch_upstream = 'origin'

    registry: dict[str, type['VcsHelper']] = {}

    def __init_subclass__(cls):
        alias = cls.alias
        assert alias

        cls.registry[alias] = cls

        super().__init_subclass__()

    def __init__(self):
        self.remote = None

    @classmethod
    def get(cls, vcs_path: str | None = None) -> 'VcsHelper | None':
        """Returns an appropriate VCS helper object.
        
        :param vcs_path: Repository dir

        """
        vcs_path = vcs_path or os.getcwd()

        helper = None

        for helper_cls in cls.registry.values():
            if os.path.exists(os.path.join(vcs_path, f'.{helper_cls.alias}')):
                helper = helper_cls()
                break

        return helper

    def run_command(self, command: str | Sequence[str]):
        """Run a VCS command without invoking a shell."""
        if isinstance(command, str):
            command = shlex.split(command)
        return run_command([self.alias, *command])

    def init(self):
        """Initializes a repository."""
        return self.run_command(['init', '-q'])

    def get_modified(self) -> list[str]:
        """Returns modified filepaths."""

        lines = self.run_command(['status', '-s'])
        modified = []

        for line in lines:
            marker, filepath = line.split(' ', 1)
            if 'M' in marker:
                modified.append(filepath)

        return modified

    def get_current_branch(self) -> str:
        """Return the current branch, including an unborn branch."""
        try:
            data = self.run_command(['symbolic-ref', '--quiet', '--short', 'HEAD'])
        except CommandError as e:
            raise ProjectorExeption(
                'VCS needs to be on a named branch.'
            ) from e

        if not data:
            raise ProjectorExeption('Unable to determine the current VCS branch.')

        return data[0]

    def check(self):
        """Perform a basic VCS check."""
        self.get_current_branch()

    def add_tag(self, name: str, description: str, *, overwrite: bool = False):
        """Adds a tag.

        :param name: Tag name
        :param description: Additional description
        :param overwrite: Whether to overwrite tag if exists.

        """
        overwrite = '-f' if overwrite else ''

        with NamedTemporaryFile() as f:
            f.write(description.encode())
            f.flush()

            self.run_command(['tag', name, *([overwrite] if overwrite else []), '-F', f.name])

    def add(self, filename: list[str] | str | list[Path] | Path = None):
        """Adds a file into a changelist.

        :param filename: If not provided all files in working tree are added.

        """
        if filename is None:
            filenames = []
        elif isinstance(filename, (str, Path)):
            filenames = [filename]
        else:
            filenames = filename

        self.run_command(['add', *map(str, filenames)])

    def commit(self, message: str):
        """Commits files added to changelist.

        :param message: Commit description.

        """
        with NamedTemporaryFile() as f:
            f.write(message.encode())
            f.flush()

            self.run_command(['commit', '-F', f.name])

    def get_remotes(self):
        """Returns a list of remotes."""
        return self.run_command(['remote'])

    def pull(self):
        """Pulls updates from remotes."""
        try:
            self.run_command(['pull'])

        except CommandError:
            # Fail if no remotes is OK.

            if self.get_remotes():
                raise

    def add_remote(self, address: str, *, alias: str = 'origin'):
        """Adds a remote repository.
        
        :param address:
        :param alias:

        """
        self.remote = address

    def push(self, *, upstream: bool | str = None):
        """Pushes local changes and tags to remote.
        
        :param upstream: Upstream alias. If True, default name is used.

        """
        if upstream:

            if upstream is True:
                upstream = self.branch_upstream

            self.run_command(['push', '-u', upstream, self.get_current_branch()])

        else:
            self.run_command(['push'])

        self.run_command(['push', '--tags'])


class GitHelper(VcsHelper):
    """Encapsulates Git related commands."""

    title = 'Git'
    alias = 'git'

    def add_remote(self, address: str, *, alias: str = 'origin'):
        """Adds a remote repository.

        :param address:
        :param alias:

        """
        super().add_remote(address, alias=alias)

        self.run_command(['remote', 'add', alias, address])

    def add(self, filename: Path | str = None):
        """Adds a file into a changelist.

        :param filename: If not provided all files in working tree are added.

        """
        filename = filename or '.'

        super().add(filename)
