import os
from tempfile import NamedTemporaryFile
from typing import Optional, List, Union

from ..exceptions import ProjectorExeption, CommandError
from ..utils import run_command


class VcsHelper:
    """Base helper for VCS related actions."""

    TITLE = None
    MASTER = 'master'
    UPSTREAM = 'origin'
    COMMAND = None

    def __init__(self):
        self.remote = None

    @classmethod
    def get_backends(cls) -> dict:
        """Returns available backends."""

        backends = {}

        for backend in (GitHelper, MercurialHelper):
            backends[backend.COMMAND] = backend

        return backends

    @classmethod
    def get(cls, vcs_path: Optional[str] = None) -> 'VcsHelper':
        """Returns an appropriate VCS helper object.
        
        :param vcs_path: Repository dir

        """
        vcs_path = vcs_path or os.getcwd()

        helper = None

        for helper_cls in cls.get_backends().values():
            if os.path.exists(os.path.join(vcs_path, f'.{helper_cls.COMMAND}')):
                helper = helper_cls()
                break

        return helper

    def run_command(self, command):
        """Basic command runner to implement."""
        return run_command(f'{self.COMMAND} {command}')

    def init(self):
        """Initializes a repository."""
        return self.run_command('init -q')

    def get_modified(self) -> List[str]:
        """Returns modified filepaths."""

        lines = self.run_command('status -s')
        modified = []

        for line in lines:
            marker, filepath = line.split(' ', 1)
            if 'M' in marker:
                modified.append(filepath)

        return modified

    def check(self):
        """Performs basic vcs check."""
        data = self.run_command('branch')

        if f'* {self.MASTER}' not in ''.join(data):
            raise ProjectorExeption(
                f'VCS needs to be initialized and branch set to `{self.MASTER}`')

    def add_tag(self, name: str, description: str, *, overwrite: bool = False):
        """Adds a tag.

        :param name: Tag name
        :param description: Additional description
        :param overwrite: Whether to overwrite tag if exists.

        """
        overwrite = '-f' if overwrite else ''

        if isinstance(description, str):
            description = description.encode('utf8')

        with NamedTemporaryFile() as f:
            f.write(description)
            f.flush()

            self.run_command(f'tag {name} {overwrite} -F {f.name}')

    def add(self, filename: Union[List[str], str] = None):
        """Adds a file into a changelist.

        :param filename: If not provided all files in working tree are added.

        """
        filename = filename or []
        if isinstance(filename, list):
            filename = ' '.join(filename)

        filename = filename.strip() or ''

        self.run_command(f'add {filename}')

    def commit(self, message: str):
        """Commits files added to changelist.

        :param message: Commit description.

        """
        self.run_command("commit -m '%s'" % message.replace("'", "''"))

    def get_remotes(self):
        """Returns a list of remotes."""
        return self.run_command('remote')

    def pull(self):
        """Pulls updates from remotes."""
        try:
            self.run_command('pull')

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

    def push(self, *, upstream: Union[bool, str] = None):
        """Pushes local changes and tags to remote.
        
        :param upstream: Upstream alias. If True, default name is used.

        """
        if upstream:

            if upstream is True:
                upstream = self.UPSTREAM

            self.run_command(f'push -u {upstream} {self.MASTER}')

        else:
            self.run_command('push')

        self.run_command('push --tags')


class GitHelper(VcsHelper):
    """Encapsulates Git related commands."""

    TITLE = 'Git'
    COMMAND = 'git'

    def add_remote(self, address: str, *, alias: str = 'origin'):
        """Adds a remote repository.

        :param address:
        :param alias:

        """
        super().add_remote(address, alias=alias)

        self.run_command(f'remote add {alias} {address}')

    def add(self, filename: str = None):
        """Adds a file into a changelist.

        :param filename: If not provided all files in working tree are added.

        """
        filename = filename or '.'

        super().add(filename)


class MercurialHelper(VcsHelper):
    """Encapsulates Mercurial related commands."""

    TITLE = 'Mercurial'
    COMMAND = 'hg'

    def get_remotes(self):
        """Returns a list of remotes."""
        return []

    def push(self, *, upstream: Union[bool, str] = None):
        """Pushes local changes and tags to remote.

        :param upstream: Upstream URL. If True, remote URL is used.

        """
        if upstream is True and self.remote:
            upstream = self.remote

        super().push(upstream=upstream)
