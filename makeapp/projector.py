from __future__ import unicode_literals
import os
import io
import logging
from subprocess import Popen, PIPE
from contextlib import contextmanager

from setuptools import find_packages

class MakeappException(Exception):
    """Base makeapp exception."""


class AppMakerException(MakeappException):
    """Basic AppMaker related exception."""


class ProjectorExeption(MakeappException):
    """Basic Projector related exception."""


class CommandError(MakeappException):
    """Raised when projector detects external process invocation error."""


class NoChanges(ProjectorExeption):
    """Raised when a release attepted with no changes registered."""


LOG = logging.getLogger(__name__)


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


class GitHelper(object):
    """Encapsulates Git related commands."""

    @classmethod
    def run_command(cls, command):
        """Basic git command runner."""
        return run_command('git %s' % command)

    @classmethod
    def check(cls):
        """Performs basic vcs check."""
        data = cls.run_command('branch')
        if '* master' not in ''.join(data):
            raise ProjectorExeption('VCS needs to be initialized and branch set to `master`')

    @classmethod
    def add_tag(cls, name, description, overwrite=False):
        """Adds a tag.

        :param str|unicode name: Tag name
        :param str|unicode description: Additional description
        :param bool overwrite: Whether to overwrite tag if exists.
        """
        overwrite = '-f' if overwrite else ''
        cls.run_command("tag %s %s -m '%s'" % (name, overwrite, description))

    @classmethod
    def add(cls, filename):
        """Adds a file into a changelist.

        :param str|unicode filename:
        """
        cls.run_command('add %s' % filename)

    @classmethod
    def commit(cls, message):
        """Commits files added to changelist.

        :param str|unicode message: Commit description.
        """
        cls.run_command("commit -m '%s'" % message)

    @classmethod
    def pull(cls):
        """Pulls updates from remotes."""
        cls.run_command('pull')

    @classmethod
    def push(cls):
        """Pushes local changes and tags to remote."""
        cls.run_command('push')
        cls.run_command('push --tags')


VCS_HELPER = GitHelper


class DistHelper(object):
    """Encapsulates Python distribution related logic."""

    @classmethod
    def run_command(cls, command):
        """Basic command runner."""
        return run_command('python setup.py %s' % command)

    @classmethod
    def upload(cls):
        """Builds a package and uploads it to PyPI."""
        cls.run_command('clean --all sdist bdist_wheel upload')


class FileHelper(object):
    """Encapsulates file related functions."""

    __slots__ = ['filepath', 'line_idx', 'contents']

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

    def vcs_add(self):
        """Adds current file to VCS changelist."""
        VCS_HELPER.add(self.filepath)

    def vcs_commit(self, message):
        """Commits current file and other from current changelist to VCS."""
        VCS_HELPER.commit(message)

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


class InfoBase(object):
    """Base for information gathering classes."""

    def __init__(self, file_helper):
        """
        :param FileHelper file_helper:
        """
        self.file_helper = file_helper

    def write(self):
        """Writes file changes to FS."""
        self.file_helper.write()

    def vcs_add(self):
        """Adds file to VCS changelist."""
        self.file_helper.vcs_add()


class InfoPackage(InfoBase):
    """Information gathered from application package."""

    __slots__ = ['version', 'file_helper', 'version_increment']

    VERSION_STR = 'VERSION'

    def __init__(self, file_helper, version):
        """
        :param FileHelper file_helper:
        :param tuple version: Version number tuple
        """
        super(InfoPackage, self).__init__(file_helper)
        self.version = version
        self.version_increment = 'patch'

    @classmethod
    def gather(cls, package_name):
        """Gathers information from a package,

        :param str|unicode package_name:
        :rtype: InfoPackage
        """
        LOG.debug('Getting version from `%s` package ...', package_name)

        filepath = os.path.join(package_name, '__init__.py')

        if not os.path.isfile(filepath):
            raise ProjectorExeption('Package `__init__` file not found')

        init_file = FileHelper.read_file(filepath)

        version_str = cls.VERSION_STR
        version_line_idx = None
        for idx, line in enumerate(init_file):
            if line.startswith(version_str):
                version_line_idx = idx
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in init file')

        fake_locals = {}
        exec (init_file[version_line_idx], {}, fake_locals)

        version = fake_locals[version_str]
        if not isinstance(version, tuple):
            raise ProjectorExeption('Unsupported version format: %s', version)

        LOG.info('Current version from package: `%s`', version)

        result = InfoPackage(
            version=version,
            file_helper=FileHelper(
                filepath=filepath,
                line_idx=version_line_idx,
                contents=init_file
            )
        )
        return result

    def get_next_version(self):
        """Calculates and returns next version number tuple.

        :rtype: tuple
        """
        increment = self.version_increment

        chunks = ('major', 'minor', 'patch')
        if increment not in chunks:
            raise ProjectorExeption(
                'Unsupported version chunk to increment: `%s`. Should be one of: %s' % (increment, chunks))

        version_old = self.version
        version_new = []

        chunk_idx = chunks.index(increment)
        for idx, val in enumerate(version_old):
            if idx == chunk_idx:
                val += 1
            elif idx > chunk_idx:
                val = 0
            version_new.append(val)

        return tuple(version_new)

    def version_bump(self, increment='patch'):
        """Bumps version number.
        Returns new version number tuple.

        :param str|unicode increment: Increment part (major, minor, patch)
        :rtype: tuple
        """
        self.version_increment = increment

        version_old = self.version
        version_new = self.get_next_version()
        self.version = version_new

        LOG.info('Version `%s` bumped to `%s`', version_old, version_new)

        self.file_helper.line_replace('%s = (%s)' % (self.VERSION_STR, ', '.join(map(str, version_new))))

        return version_new


class InfoChangelog(InfoBase):
    """Information gathered from changelog file."""

    __slots__ = ['file_helper', '_changes']

    FILENAME_CHANGELOG = 'CHANGELOG'
    UNRELEASED_STR = 'Unreleased'

    @classmethod
    def gather(cls):
        """Gathers information from a changelog.

        :rtype: InfoChangelog
        """
        filepath = cls.FILENAME_CHANGELOG

        LOG.debug('Getting changelog from `%s` ...', os.path.basename(filepath))

        if not os.path.isfile(filepath):
            raise ProjectorExeption('Changelog file not found')

        changelog = FileHelper.read_file(filepath)

        if not changelog[1].startswith('=='):
            raise ProjectorExeption('Unexpected changelog file format')

        unreleased_str = cls.UNRELEASED_STR
        unreleased_entry_exists = False
        version_line_idx = None
        for supposed_line_idx in (3, 4, 5):
            line = changelog[supposed_line_idx]
            unreleased_entry_exists = line == unreleased_str
            if unreleased_entry_exists or line.startswith('v'):
                version_line_idx = supposed_line_idx
                LOG.info('Current version from changelog: `%s`', line)
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in changelog')

        if not unreleased_entry_exists:
            changelog[version_line_idx:version_line_idx] = [
                unreleased_str,
                '-' * len(unreleased_str),
                '', ''
            ]

        # Normalize.
        if version_line_idx == 3:
            changelog.insert(3, '')
            version_line_idx = 4

        result = InfoChangelog(
            file_helper=FileHelper(
                filepath=filepath,
                line_idx=version_line_idx,
                contents=changelog
            )
        )

        return result

    def commit(self):
        """Commits a new changelog into VCS."""
        helper = self.file_helper
        helper.write()
        helper.vcs_add()
        helper.vcs_commit('%s updated' % self.FILENAME_CHANGELOG)

    def deduce_version_increment(self):
        """Deduces version increment chunk from a changelog.

        :return: major, minor, patch
        :rtype: str|unicode
        """
        supposed_chunk = 'patch'

        for change in self.get_changes():
            if change.startswith('+'):  # todo "-" major?
                supposed_chunk = 'minor'
                break
        return supposed_chunk

    def version_bump(self, new_version):
        """Bumps version number.

        Returns version number string as in changelog.

        :param tuple new_version:
        :rtype: str|unicode
        """
        version_str = 'v%s' % '.'.join(map(str, new_version))

        self.file_helper.line_replace(version_str)
        self.file_helper.line_replace('-' * len(version_str), offset=1)

        return version_str

    def add_change(self, description):
        """Adds change into changelog.

        :param str|unicode description:
        """
        if not description:
            return

        if description[0] not in ('*', '-', '+'):
            description = '* %s' % description

        self.file_helper.insert(description, offset=2)

    def get_changes(self):
        """Returns a list of new version changes from a changelog.

        :rtype: list
        """
        changes = []
        for line in self.file_helper.iter_after(offset=2):
            if not line.strip():
                break
            changes.append(line)
        return changes


class Project(object):
    """Encapsulates project related logic."""

    def __init__(self, project_path):
        """
        :param str|unicode project_path: Project root (containing setup.py) path.
        """
        self.project_path = project_path
        self.info_package = None  # type: InfoPackage
        self.info_changelog = None  # type: InfoChangelog

        with self.chdir():
            self.gather_data()

    @contextmanager
    def chdir(self):
        """Temporarily changes current working directory."""
        curr_dir = os.getcwd()
        os.chdir(self.project_path)
        try:
            yield

        finally:
            os.chdir(curr_dir)

    def gather_data(self):
        """Gathers data relevant for project related functions."""
        project_dirname = self.project_path
        LOG.info('Gathering info from `%s` directory ...', project_dirname)

        if not os.path.isfile('setup.py'):
            raise ProjectorExeption('No `setup.py` file found')

        VCS_HELPER.check()

        packages = find_packages()
        main_package = packages[0]

        self.info_package = InfoPackage.gather(main_package)
        self.info_changelog = InfoChangelog.gather()

    def release(self, increment=None, changelog_entry=None, upload=True):
        """Makes package release.

        * Bumps version number
        * Adds changelog info
        * Tags VCS
        * Pushes to remote repository
        * Publishes on PyPI

        :param str|unicode increment: Version chunk to increment (major, minor, patch)
            If not set, will be deduced from changelog info.

        :param str|unicode changelog_entry: Message to add to changelog.

        :param bool upload: Upload to repository and PyPI
        """
        with self.chdir():
            VCS_HELPER.pull()

        package = self.info_package
        changelog = self.info_changelog

        if changelog_entry:
            self.add_change(changelog_entry)

        increment = increment or changelog.deduce_version_increment()

        new_version = package.version_bump(increment)
        new_version_str = changelog.version_bump(new_version)

        version_summary = '\n'.join(changelog.get_changes())
        version_summary = version_summary.strip()

        if not version_summary.strip():
            raise NoChanges('No changes detected. Please add changes before release')

        LOG.info('Version summary:\n%s' % version_summary)

        with self.chdir():

            for info in [package, changelog]:
                info.write()
                info.vcs_add()

            LOG.info('Fixating VCS changes ...')

            VCS_HELPER.commit('Release %s' % new_version_str)
            VCS_HELPER.add_tag(new_version_str, version_summary, overwrite=True)

        upload and self.upload()

        LOG.info('Version `%s` released' % new_version_str)

    def add_change(self, description):
        """Add a change into changelog.

        :param str|unicode description:
        """
        LOG.debug('Adding change ...')  # todo commit all staged?

        with self.chdir():
            changelog = self.info_changelog
            changelog.add_change(description)
            changelog.commit()

    def upload(self):
        """Uploads project data to remote repository Python Package Index server."""
        LOG.info('Uploading package ...')

        with self.chdir():
            VCS_HELPER.push()
            DistHelper.upload()
