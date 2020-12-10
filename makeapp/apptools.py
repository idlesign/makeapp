import logging
import os
from datetime import datetime
from typing import Tuple, List, Optional, Union

from setuptools import find_packages

from .exceptions import ProjectorExeption
from .helpers.dist import DistHelper
from .helpers.files import FileHelper
from .helpers.vcs import VcsHelper
from .utils import chdir

LOG = logging.getLogger(__name__)


VERSION_NUMBER_CHUNKS = ('major', 'minor', 'patch')


class DataContainer:
    """Base for information gathering classes."""

    def __init__(self, file_helper: FileHelper):
        """
        :param file_helper:

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

    def __init__(self, file_helper: FileHelper, version: Tuple[int, ...]):
        """
        :param file_helper:
        :param version: Version number tuple

        """
        super().__init__(file_helper)
        self.version_current = version
        self.version_next = None
        self.version_increment = 'patch'

    @classmethod
    def get_version_str(cls, version: Tuple[int, ...]) -> str:
        """Return string representation for a given version.
        
        :param version:

        """
        return '.'.join(map(str, version))

    @property
    def version_current_str(self):
        return self.get_version_str(self.version_current)

    @property
    def version_next_str(self):
        return self.get_version_str(self.version_next)

    @classmethod
    def get(cls, package_name: str) -> 'PackageData':
        """Gathers information from a package,

        :param package_name:

        """
        LOG.debug(f'Getting version from `{package_name}` package ...')

        filepath = os.path.join(package_name, '__init__.py')

        if not os.path.isfile(filepath):
            raise ProjectorExeption("Package's `__init__` file is not found.")

        init_file = FileHelper.read_file(filepath)

        version_str = cls.VERSION_STR
        version_line_idx = None
        for idx, line in enumerate(init_file):
            if line.startswith(version_str):
                version_line_idx = idx
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in init file.')

        fake_locals = {}
        exec(init_file[version_line_idx], {}, fake_locals)

        version = fake_locals[version_str]

        if not isinstance(version, tuple):
            raise ProjectorExeption(f'Unsupported version format: {version}.')

        LOG.info(f'Current version from package: `{version}`')

        result = PackageData(
            version=version,
            file_helper=FileHelper(
                filepath=filepath,
                line_idx=version_line_idx,
                contents=init_file
            )
        )
        return result

    def get_next_version(self) -> Tuple[int, ...]:
        """Calculates and returns next version number tuple."""

        increment = self.version_increment

        if increment not in VERSION_NUMBER_CHUNKS:

            raise ProjectorExeption(
                f'Unsupported version chunk to increment: `{increment}`. '
                f'Should be one of: {VERSION_NUMBER_CHUNKS}.')

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

    def version_bump(self, increment: str = 'patch') -> Tuple[int, ...]:
        """Bumps version number.
        Returns new version number tuple.

        :param increment: Version number chunk to increment  (major, minor, patch)

        """
        self.version_increment = increment

        version_current = self.version_current
        version_new = self.get_next_version()

        LOG.info(f'Version `{version_current}` bumped to `{version_new}`')

        self.file_helper.line_replace(f"{self.VERSION_STR} = ({', '.join(map(str, version_new))})")

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
    def get(cls) -> 'ChangelogData':
        """Gathers information from a changelog."""

        filepath = cls.FILENAME_CHANGELOG

        LOG.debug(f'Getting changelog from `{os.path.basename(filepath)}` ...')

        if not os.path.isfile(filepath):
            raise ProjectorExeption('Changelog file not found.')

        changelog = FileHelper.read_file(filepath)

        if not changelog[1].startswith('=='):
            raise ProjectorExeption('Unexpected changelog file format.')

        unreleased_str = cls.UNRELEASED_STR
        unreleased_entry_exists = False
        version_line_idx = None

        for supposed_line_idx in (3, 4, 5):
            line = changelog[supposed_line_idx]
            unreleased_entry_exists = line == unreleased_str

            if unreleased_entry_exists or line.startswith('v'):
                version_line_idx = supposed_line_idx
                LOG.info(f'Current version from changelog: `{line}`')
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in the changelog.')

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

    def deduce_version_increment(self) -> str:
        """Deduces version increment chunk from a changelog.

        Changelog bullets:
            * changed/fixed
            + new/feature
            - removed

        Deduction rules:
            By default `patch` chunk is incremented.
            If any + entries `minor` is incremented.

        Returns: major, minor, patch

        """
        supposed_chunk = 'patch'

        for change in self.get_changes():
            if change.startswith('+'):
                supposed_chunk = 'minor'
                break
        return supposed_chunk

    def version_bump(self, new_version: Tuple[int, ...]) -> str:
        """Bumps version number.

        Returns version number string as in changelog.

        :param new_version:

        """
        version_str = f"v{'.'.join(map(str, new_version))}"
        version_with_date = f"{version_str} [{datetime.now().strftime('%Y-%m-%d')}]"

        replace = self.file_helper.line_replace

        replace(version_with_date)
        replace('-' * len(version_with_date), offset=1)

        return version_str

    def add_change(self, description: str):
        """Adds change into changelog.

        :param description:

        """
        if not description:
            return

        if description[0] not in self.PREFIXES:
            description = f'* {description}'

        self.file_helper.insert(description, offset=2)

    def get_changes(self) -> List[str]:
        """Returns a list of new version changes from a changelog."""

        changes = []

        for line in self.file_helper.iter_after(offset=2):

            if not line.strip():
                break

            changes.append(line)

        return changes

    def get_version_summary(self) -> str:
        """Return version summary string."""

        return '\n'.join(self.get_changes()).strip()

    def sort_version_changes(self):
        """Sorts changes of latest version inplace."""

        priorities = {prefix: priority for priority, prefix in enumerate(self.PREFIXES)}

        def sorter(line):
            line = line.lower().replace('\'"`', '')
            priority = priorities.get(line[0], 3)
            return f'{priority} {line}'

        for line_offset, change in enumerate(sorted(self.get_changes(), key=sorter), 2):
            self.file_helper.line_replace(change, offset=line_offset)

    def write(self):
        self.sort_version_changes()
        super().write()


class Project:
    """Encapsulates application (project) related logic."""

    def __init__(self, project_path: str = None):
        """
        :param project_path: Application root (containing setup.py) path.

        """
        self.project_path = project_path or os.getcwd()
        self.package: Optional[PackageData] = None
        self.changelog: Optional[ChangelogData] = None
        self.vcs = VcsHelper.get(project_path)

        with chdir(self.project_path):
            self._gather_data()

    def _gather_data(self):
        """Gathers data relevant for project related functions."""
        project_path = self.project_path

        LOG.debug(f'Gathering info from `{project_path}` directory ...')

        if not os.path.isfile('setup.py'):
            raise ProjectorExeption('No `setup.py` file found in the current directory.')

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

        LOG.debug(f'Found packages: {packages}')

        main_package = packages[0]

        self.package = PackageData.get(main_package)
        self.changelog = ChangelogData.get()

    def pull(self):
        """Pulls changes from a remote repository"""
        with chdir(self.project_path):
            self.vcs.pull()

    def get_release_info(self, increment: Optional[str] = None) -> Tuple[str, str]:
        """Returns release info tuple as part of release preparation.
        
        :param increment: Version chunk to increment (major, minor, patch)
            If not set, will be deduced from changelog data.

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

            vcs.commit(f'Release {next_version_str}')

            vcs.add_tag(next_version_str, version_summary, overwrite=True)

    def add_change(self, descriptions: Union[List[str], Tuple[str, ...], str], *, stage_modified: bool = True):
        """Add a change description into changelog.

        :param descriptions: Single change description.
            Or multiple changes descriptions in list or tuple.

        :param stage_modified: Whether to stage modified files to commit.

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

            commit_message = f'{changelog.FILENAME_CHANGELOG} updated'

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
