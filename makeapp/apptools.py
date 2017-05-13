from __future__ import unicode_literals
import os
import logging

from setuptools import find_packages

from .helpers.vcs import VcsHelper
from .helpers.files import FileHelper
from .helpers.dist import DistHelper
from .exceptions import ProjectorExeption, NoChanges
from .utils import chdir

LOG = logging.getLogger(__name__)


class DataContainer(object):
    """Base for information gathering classes."""

    def __init__(self, file_helper):
        """
        :param FileHelper file_helper:
        """
        self.file_helper = file_helper

    @property
    def filepath(self):
        return self.file_helper.filepath

    @classmethod
    def get(cls, *args, **kwargs):
        raise NotImplementedError()

    def write(self):
        """Writes file changes to FS."""
        self.file_helper.write()


class PackageData(DataContainer):
    """Information gathered from application _package."""

    VERSION_STR = 'VERSION'

    def __init__(self, file_helper, version):
        """
        :param FileHelper file_helper:
        :param tuple version: Version number tuple
        """
        super(PackageData, self).__init__(file_helper)
        self.version = version
        self.version_increment = 'patch'

    @classmethod
    def get(cls, package_name):
        """Gathers information from a _package,

        :param str|unicode package_name:
        :rtype: PackageData
        """
        LOG.debug('Getting version from `%s` _package ...', package_name)

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

        LOG.info('Current version from _package: `%s`', version)

        result = PackageData(
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


class ChangelogData(DataContainer):
    """Information gathered from _changelog file."""

    FILENAME_CHANGELOG = 'CHANGELOG'
    UNRELEASED_STR = 'Unreleased'

    @classmethod
    def get(cls):
        """Gathers information from a _changelog.

        :rtype: ChangelogData
        """
        filepath = cls.FILENAME_CHANGELOG

        LOG.debug('Getting _changelog from `%s` ...', os.path.basename(filepath))

        if not os.path.isfile(filepath):
            raise ProjectorExeption('Changelog file not found')

        changelog = FileHelper.read_file(filepath)

        if not changelog[1].startswith('=='):
            raise ProjectorExeption('Unexpected _changelog file format')

        unreleased_str = cls.UNRELEASED_STR
        unreleased_entry_exists = False
        version_line_idx = None
        for supposed_line_idx in (3, 4, 5):
            line = changelog[supposed_line_idx]
            unreleased_entry_exists = line == unreleased_str
            if unreleased_entry_exists or line.startswith('v'):
                version_line_idx = supposed_line_idx
                LOG.info('Current version from _changelog: `%s`', line)
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in _changelog')

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

        result = ChangelogData(
            file_helper=FileHelper(
                filepath=filepath,
                line_idx=version_line_idx,
                contents=changelog
            )
        )

        return result

    def deduce_version_increment(self):
        """Deduces version increment chunk from a _changelog.

        Changelog bullets:
            * changed/fixed
            + new/feature
            - removed

        Deduction rules:
            By default `patch` chunk is incremented.
            If any + entries `minor` is incremented.

        :return: major, minor, patch
        :rtype: str|unicode
        """
        supposed_chunk = 'patch'

        for change in self.get_changes():
            if change.startswith('+'):
                supposed_chunk = 'minor'
                break
        return supposed_chunk

    def version_bump(self, new_version):
        """Bumps version number.

        Returns version number string as in _changelog.

        :param tuple new_version:
        :rtype: str|unicode
        """
        version_str = 'v%s' % '.'.join(map(str, new_version))

        self.file_helper.line_replace(version_str)
        self.file_helper.line_replace('-' * len(version_str), offset=1)

        return version_str

    def add_change(self, description):
        """Adds change into _changelog.

        :param str|unicode description:
        """
        if not description:
            return

        if description[0] not in ('*', '-', '+'):
            description = '* %s' % description

        self.file_helper.insert(description, offset=2)

    def get_changes(self):
        """Returns a list of new version changes from a _changelog.

        :rtype: list
        """
        changes = []
        for line in self.file_helper.iter_after(offset=2):
            if not line.strip():
                break
            changes.append(line)
        return changes


class Application(object):
    """Encapsulates application (project) related logic."""

    def __init__(self, project_path):
        """
        :param str|unicode project_path: Application root (containing setup.py) path.
        """
        self._project_path = project_path
        self._package = None  # type: PackageData
        self._changelog = None  # type: ChangelogData
        self._vcs = VcsHelper.get(project_path)

        with chdir():
            self._gather_data()

    def _gather_data(self):
        """Gathers data relevant for application related functions."""
        project_dirname = self._project_path
        LOG.info('Gathering info from `%s` directory ...', project_dirname)

        if not os.path.isfile('setup.py'):
            raise ProjectorExeption('No `setup.py` file found')

        self._vcs.check()

        packages = find_packages()
        main_package = packages[0]

        self._package = PackageData.get(main_package)
        self._changelog = ChangelogData.get()

    def release(self, increment=None, changelog_entry=None, upload=True):
        """Makes package release.

        * Bumps version number
        * Adds changelog info
        * Tags VCS
        * Pushes to remote repository
        * Publishes on PyPI

        :param str|unicode increment: Version chunk to increment (major, minor, patch)
            If not set, will be deduced from _changelog info.

        :param str|unicode changelog_entry: Message to add to _changelog.

        :param bool upload: Upload to repository and PyPI
        """
        with chdir():
            self._vcs.pull()

        package = self._package
        changelog = self._changelog
        vcs = self._vcs

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

        with chdir():

            for info in (package, changelog):
                info.write()
                vcs.add(info.filepath)

            LOG.info('Commit VCS changes ...')

            vcs.commit('Release %s' % new_version_str)
            vcs.add_tag(new_version_str, version_summary, overwrite=True)

        upload and self.upload()

        LOG.info('Version `%s` released' % new_version_str)

    def add_change(self, description):
        """Add a change into _changelog.

        :param str|unicode description:
        """
        LOG.debug('Adding change ...')  # todo commit all staged?

        with chdir():
            changelog = self._changelog
            changelog.add_change(description)
            changelog.write()

            self._vcs.add(changelog.filepath)
            self._vcs.commit('%s updated' % changelog.FILENAME_CHANGELOG)

    def upload(self):
        """Uploads project data to remote repository Python Package Index server."""
        LOG.info('Uploading data ...')

        with chdir():
            self._vcs.push()
            DistHelper.upload()
