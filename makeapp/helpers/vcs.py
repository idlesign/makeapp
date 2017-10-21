import os
from collections import OrderedDict
from tempfile import NamedTemporaryFile

from jinja2 import _compat

from ..utils import run_command
from ..exceptions import ProjectorExeption, CommandError


class VcsHelper(object):
    """Base helper for VCS related actions."""

    TITLE = None
    MASTER = 'master'
    UPSTREAM = 'origin'
    COMMAND = None

    def __init__(self):
        self.remote = None

    @classmethod
    def get_backends(cls):
        """Returns available backends.
        
        :rtype: OrderedDict 
        """
        backends = OrderedDict()

        for backend in (GitHelper, MercurialHelper):
            backends[backend.COMMAND] = backend

        return backends

    @classmethod
    def get(cls, vcs_path=None):
        """Returns an appropriate VCS helper object.
        
        :param str|unicode vcs_path: Repository dir 
        :rtype: VcsHelper 
        """
        vcs_path = vcs_path or os.getcwd()

        helper = None
        for helper_cls in cls.get_backends().values():
            if os.path.exists(os.path.join(vcs_path, '.%s' % helper_cls.COMMAND)):
                helper = helper_cls()
                break

        return helper

    def run_command(self, command):
        """Basic command runner to implement."""
        return run_command('%s %s' % (self.COMMAND, command))

    def init(self):
        """Initializes a repository."""
        return self.run_command('init -q')

    def get_modified(self):
        """Returns modified filepaths.
        
        :rtype: list 
        """
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
        if '* %s' % self.MASTER not in ''.join(data):
            raise ProjectorExeption('VCS needs to be initialized and branch set to `%s`' % self.MASTER)

    def add_tag(self, name, description, overwrite=False):
        """Adds a tag.

        :param str|unicode name: Tag name
        :param str|unicode description: Additional description
        :param bool overwrite: Whether to overwrite tag if exists.
        """
        overwrite = '-f' if overwrite else ''

        if _compat.PY2:
            description = description.encode('utf8')

        with NamedTemporaryFile() as f:
            f.write(description)
            f.flush()

            self.run_command('tag %s %s -F %s' % (name, overwrite, f.name))

    def add(self, filename=None):
        """Adds a file into a changelist.

        :param str|unicode|list filename: If not provided all files in working tree are added.
        """
        filename = filename or []
        if isinstance(filename, list):
            filename = ' '.join(filename)

        filename = filename.strip() or ''

        self.run_command('add %s' % filename)

    def commit(self, message):
        """Commits files added to changelist.

        :param str|unicode message: Commit description.
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

    def add_remote(self, address, alias='origin'):
        """Adds a remote repository.
        
        :param str|unicode address: 
        :param str|unicode alias: 
        """
        self.remote = address

    def push(self, upstream=None):
        """Pushes local changes and tags to remote.
        
        :param str|unicode|bool upstream: Upstream alias. If True, default name is used. 
        """
        if upstream:
            if upstream is True:
                upstream = self.UPSTREAM
            self.run_command('push -u %s %s' % (upstream, self.MASTER))

        else:
            self.run_command('push')

        self.run_command('push --tags')


class GitHelper(VcsHelper):
    """Encapsulates Git related commands."""

    TITLE = 'Git'
    COMMAND = 'git'

    def add_remote(self, address, alias='origin'):
        """Adds a remote repository.

        :param str|unicode address: 
        :param str|unicode alias: 
        """
        super(GitHelper, self).add_remote(address, alias)
        self.run_command('remote add %s %s' % (alias, address))

    def add(self, filename=None):
        """Adds a file into a changelist.

        :param str|unicode filename: If not provided all files in working tree are added.
        """
        filename = filename or '.'
        super(GitHelper, self).add(filename)


class MercurialHelper(VcsHelper):
    """Encapsulates Mercurial related commands."""

    TITLE = 'Mercurial'
    COMMAND = 'hg'

    def get_remotes(self):
        """Returns a list of remotes."""
        return []

    def push(self, upstream=None):
        """Pushes local changes and tags to remote.

        :param str|unicode|bool upstream: Upstream URL. If True, remote URL is used. 
        """
        if upstream is True and self.remote:
            upstream = self.remote

        super(MercurialHelper, self).push(upstream)
