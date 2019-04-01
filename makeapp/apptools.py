from __future__ import unicode_literals
import os
import logging

from setuptools import find_packages

from .helpers.vcs import VcsHelper
from .helpers.files import FileHelper
from .helpers.dist import DistHelper
from .exceptions import ProjectorExeption
from .utils import chdir


LOG = logging.getLogger(__name__)


VERSION_NUMBER_CHUNKS = ('major', 'minor', 'patch')


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
    """Information gathered from application package."""

    VERSION_STR = 'VERSION'

    def __init__(self, file_helper, version):
        """
        :param FileHelper file_helper:
        :param tuple version: Version number tuple
        """
        super(PackageData, self).__init__(file_helper)
        self.version_current = version
        self.version_next = None
        self.version_increment = 'patch'

    @classmethod
    def get_version_str(cls, version):
        """Return string representation for a given version.
        
        :param tuple version: 
        :rtype: str|unicode 
        """
        return '.'.join(map(str, version))

    @property
    def version_current_str(self):
        return self.get_version_str(self.version_current)

    @property
    def version_next_str(self):
        return self.get_version_str(self.version_next)

    @classmethod
    def get(cls, package_name):
        """Gathers information from a package,

        :param str|unicode package_name:
        :rtype: PackageData
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

        if increment not in VERSION_NUMBER_CHUNKS:
            raise ProjectorExeption(
                'Unsupported version chunk to increment: `%s`. Should be one of: %s' %
                (increment, VERSION_NUMBER_CHUNKS))

        version_old = self.version_current
        version_next = []

        chunk_idx = VERSION_NUMBER_CHUNKS.index(increment)
        for idx, val in enumerate(version_old):
            if idx == chunk_idx:
                val += 1
            elif idx > chunk_idx:
                val = 0
            version_next.append(val)

        version_next = tuple(version_next)

        self.version_next = version_next

        return version_next

    def version_bump(self, increment='patch'):
        """Bumps version number.
        Returns new version number tuple.

        :param str|unicode increment: Version number chunk to increment  (major, minor, patch)
        :rtype: tuple
        """
        self.version_increment = increment

        version_current = self.version_current
        version_new = self.get_next_version()

        LOG.info('Version `%s` bumped to `%s`', version_current, version_new)

        self.file_helper.line_replace('%s = (%s)' % (self.VERSION_STR, ', '.join(map(str, version_new))))

        return version_new


class ChangelogData(DataContainer):
    """Information gathered from changelog file."""

    PREFIXES = '!+-*'
    """Line prefixes denoting change nature.
    
    ! Important change/improvement/fix
    + New feature / addition
    - Feature deprecation / removal
    * Minor change/improvement/fix
    
    """

    FILENAME_CHANGELOG = 'CHANGELOG'
    UNRELEASED_STR = 'Unreleased'

    @classmethod
    def get(cls):
        """Gathers information from a changelog.

        :rtype: ChangelogData
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
            # Add `Unreleased` entry.
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
        """Deduces version increment chunk from a changelog.

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

        if description[0] not in self.PREFIXES:
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

    def get_version_summary(self):
        """Return version summary string.
        
        :rtype: str|unicode 
        """
        return '\n'.join(self.get_changes()).strip()

    def sort_version_changes(self):
        """Sorts changes of latest version inplace."""

        priorities = {prefix: priority for priority, prefix in enumerate(self.PREFIXES)}

        def sorter(line):
            line = line.lower().replace('\'"`', '')
            priority = priorities.get(line[0], 3)
            return '%s %s' % (priority, line)

        for line_offset, change in enumerate(sorted(self.get_changes(), key=sorter), 2):
            self.file_helper.line_replace(change, offset=line_offset)

    def write(self):
        self.sort_version_changes()
        super(ChangelogData, self).write()


class Project(object):
    """Encapsulates application (project) related logic."""

    def __init__(self, project_path=None):
        """
        :param str|unicode project_path: Application root (containing setup.py) path.
        :param bool dry_run: Do not commit changes to filesystem.
        """
        self.project_path = project_path or os.getcwd()
        self.package = None  # type: PackageData
        self.changelog = None  # type: ChangelogData
        self.vcs = VcsHelper.get(project_path)

        with chdir(self.project_path):
            self._gather_data()

    def _gather_data(self):
        """Gathers data relevant for project related functions."""
        project_path = self.project_path
        LOG.debug('Gathering info from `%s` directory ...', project_path)

        if not os.path.isfile('setup.py'):
            raise ProjectorExeption('No `setup.py` file found')

        self.vcs.check()

        packages = find_packages()

        if len(packages) > 1:
            # Try to narrow down packages list.
            # todo Seems to be error prone on edge cases (with many packages).

            parent_dirname = os.path.basename(project_path)

            if parent_dirname in packages:
                packages = [parent_dirname]

            else:
                'tests' in packages and packages.remove('tests')


        LOG.debug('Found packages: %s', packages)

        main_package = packages[0]

        self.package = PackageData.get(main_package)
        self.changelog = ChangelogData.get()

    def pull(self):
        """Pulls changes from a remote repository"""
        with chdir(self.project_path):
            self.vcs.pull()

    def get_release_info(self, increment=None):
        """Returns release info tuple as part of release preparation.
        
        :param str|unicode increment: Version chunk to increment (major, minor, patch)
            If not set, will be deduced from changelog data.
            
        :rtype: tuple 
        """
        changelog = self.changelog

        increment = increment or changelog.deduce_version_increment()

        next_version = self.package.version_bump(increment)
        next_version_str = changelog.version_bump(next_version)

        version_summary = changelog.get_version_summary()

        return next_version_str, version_summary

    def release(self, next_version_str, version_summary):
        """Makes application package release.

        * Bumps version number
        * Adds changelog info
        * Tags VCS
        """
        vcs = self.vcs

        with chdir(self.project_path):

            for info in (self.package, self.changelog):
                info.write()
                vcs.add(info.filepath)

            LOG.debug('Commit VCS changes ...')

            vcs.commit('Release %s' % next_version_str)
            vcs.add_tag(next_version_str, version_summary, overwrite=True)

    def add_change(self, descriptions, stage_modified=True):
        """Add a change description into changelog.

        :param list|tuple|str|unicode descriptions: Single change description.
            Or multiple changes descriptions in list or tuple.

        :param bool stage_modified: Whether to stage modified files to commit.

        """
        LOG.debug('Adding change ...')

        with chdir(self.project_path):
            changelog = self.changelog

            if not isinstance(descriptions, (list, tuple)):
                descriptions = [descriptions]

            for description in descriptions:

                description = description.strip(' ')

                if not description.endswith(('.', '!')):
                    description += '.'

                changelog.add_change(description)

            changelog.write()

            commit_message = '%s updated' % changelog.FILENAME_CHANGELOG

            files_to_stage = [changelog.filepath]
            if stage_modified:
                files_to_stage.extend(self.vcs.get_modified())

                if len(descriptions) == 1:
                    # Set a description as a commit message.
                    commit_message = descriptions[0].strip(changelog.PREFIXES)

            self.vcs.add(files_to_stage)
            self.vcs.commit(commit_message)

    def publish(self):
        """Uploads project data to remote VCS and Python Package Index server."""
        LOG.info('Publishing application ...')

        with chdir(self.project_path):
            self.vcs.push()
            DistHelper.upload()
