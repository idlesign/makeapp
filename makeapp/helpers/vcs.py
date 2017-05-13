import os

from ..utils import run_command
from ..exceptions import ProjectorExeption


class VcsHelper(object):
    """Base helper for VCS related actions."""

    MASTER = 'master'
    COMMAND = None

    @classmethod
    def get(cls, vcs_path=None):
        """Returns an appropriate VCS helper object.
        
        :param str|unicode vcs_path: Repository dir 
        :rtype: VcsHelper 
        """
        vcs_path = vcs_path or os.getcwd()

        helper = None
        for helper_cls in (GitHelper, MercurialHelper):
            if os.path.exists(os.path.join(vcs_path, '.%s' % helper_cls.COMMAND)):
                helper = helper_cls()
                break

        return helper

    def run_command(self, command):
        """Basic command runner to implement."""
        return run_command('%s %s' % (self.COMMAND, command))

    def check(self):
        """Performs basic _vcs check."""
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
        self.run_command("tag %s %s -m '%s'" % (name, overwrite, description))

    def add(self, filename):
        """Adds a file into a changelist.

        :param str|unicode filename:
        """
        self.run_command('add %s' % filename)

    def commit(self, message):
        """Commits files added to changelist.

        :param str|unicode message: Commit description.
        """
        self.run_command("commit -m '%s'" % message)

    def pull(self):
        """Pulls updates from remotes."""
        self.run_command('pull')

    def push(self):
        """Pushes local changes and tags to remote."""
        self.run_command('push')
        self.run_command('push --tags')


class GitHelper(VcsHelper):
    """Encapsulates Git related commands."""

    COMMAND = 'git'


class MercurialHelper(VcsHelper):
    """Encapsulates Mercurial related commands."""

    COMMAND = 'hg'
