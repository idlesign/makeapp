import logging
import os
from datetime import datetime
from pathlib import Path

from .exceptions import ProjectorExeption
from .helpers.dist import DistHelper
from .helpers.files import FileHelper
from .helpers.vcs import VcsHelper
from .helpers.venvs import VenvHelper
from .utils import chdir, configure_logging, Uv, Ruff, MkDocs

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
        raise NotImplementedError

    def write(self):
        """Writes file changes to FS."""
        self.file_helper.write()


class PackageData(DataContainer):
    """Information gathered from application package."""

    VERSION_ATTR = 'VERSION'

    def __init__(self, file_helper: FileHelper, version: tuple[int, ...]):
        """
        :param file_helper:
        :param version: Version number tuple

        """
        super().__init__(file_helper)
        self.version_current = version
        self.version_next = None
        self.version_increment = 'patch'

    @classmethod
    def get_version_str(cls, version: tuple[int, ...]) -> str:
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
    def get(cls, *, package_path: Path) -> 'PackageData':
        """Gathers information from a package,

        :param package_path:

        """
        LOG.debug(f'Getting version from `{package_path}` package ...')

        path_init = package_path / '__init__.py'
        init_file = FileHelper.read_file(path_init)

        version_attr = cls.VERSION_ATTR
        version_line_idx = None
        for idx, line in enumerate(init_file):
            if line.startswith(version_attr):
                version_line_idx = idx
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in init file.')

        version_line = init_file[version_line_idx]
        version_attr = version_line.partition('=')[-1].strip(' "\'').strip()
        version = tuple(map(int, version_attr.split('.')))

        if len(version) < 3:
            raise ProjectorExeption(f'Unsupported version format: {version}.')

        LOG.info(f'Current version from package: `{".".join(map(str, version))}`')

        result = PackageData(
            version=version,
            file_helper=FileHelper(
                filepath=path_init,
                line_idx=version_line_idx,
                contents=init_file
            )
        )
        return result

    def get_next_version(self) -> tuple[int, ...]:
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

    def version_bump(self, increment: str = 'patch') -> tuple[int, ...]:
        """Bumps version number.
        Returns new version number tuple.

        :param increment: Version number chunk to increment  (major, minor, patch)

        """
        self.version_increment = increment

        version_current = self.version_current
        version_new = self.get_next_version()

        LOG.info(f'Version `{version_current}` bumped to `{version_new}`')

        version_new_str = '.'.join(map(str, version_new))
        self.file_helper.line_replace(f"{self.VERSION_ATTR} = '{version_new_str}'")

        return version_new


class ChangelogData(DataContainer):
    """Information gathered from changelog file."""

    change_markers = '!+-*'
    """Line prefixes denoting change nature.
    
    ! Important change/improvement/fix
    + New feature / addition
    - Feature deprecation / removal
    * Minor change/improvement/fix
    
    """
    change_marker_default = '*'

    filename = 'CHANGELOG.md'
    marker_unreleased = 'Unreleased'

    _prefix_version = '### '
    _prefix_change = '* '
    _offset_change = 1

    @classmethod
    def get(cls) -> 'ChangelogData':
        """Gathers information from a changelog."""

        filepath = Path(cls.filename)

        LOG.debug(f'Getting changelog from: {filepath.name} ...')

        if not filepath.is_file():
            raise ProjectorExeption('Changelog file not found.')

        changelog = FileHelper.read_file(filepath)

        if not changelog[0].startswith('# '):
            raise ProjectorExeption('Unexpected changelog file format.')

        unreleased_str = cls.marker_unreleased
        prefix_version = cls._prefix_version
        version_line_idx = None

        for supposed_line_idx in (2, 3, 4):
            line = changelog[supposed_line_idx].lstrip('# ')
            unreleased_entry_exists = line == unreleased_str

            if unreleased_entry_exists or line.startswith('v'):
                version_line_idx = supposed_line_idx
                LOG.info(f'Current version from changelog: {line}.')
                break

        if version_line_idx is None:
            raise ProjectorExeption('Version line not found in the changelog.')

        if not unreleased_entry_exists:
            # Add `Unreleased` entry.
            changelog[version_line_idx:version_line_idx] = [
                f'{prefix_version}{unreleased_str}',
                ''
            ]

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

        Changelog markers:
            * changed/fixed
            + new/feature
            - removed

        Deduction rules:
            By default `patch` chunk is incremented.
            If any `+` entries, `minor` is incremented.

        Returns: major, minor, patch

        """
        supposed_chunk = 'patch'

        for change in self.get_changes():
            if change.startswith(f'{self._prefix_change}++'):
                supposed_chunk = 'minor'
                break
        return supposed_chunk

    def version_bump(self, new_version: tuple[int, ...]) -> str:
        """Bumps version number.

        Returns version number string as in changelog.

        :param new_version:

        """
        version_num = f"v{'.'.join(map(str, new_version))}"
        version_with_date = f"{self._prefix_version}{version_num} [{datetime.now().strftime('%Y-%m-%d')}]"

        replace = self.file_helper.line_replace

        replace(version_with_date)

        return version_num

    def add_change(self, description: str):
        """Adds change into changelog.

        :param description:

        """
        if not description:
            return

        marker = description[0]
        markers = self.change_markers

        if marker not in markers:
            marker = self.change_marker_default

        description = description.lstrip(f' {markers}')
        description = f'{self._prefix_change}{marker * 2} {description}'

        self.file_helper.insert(description, offset=self._offset_change)

    def get_changes(self) -> list[str]:
        """Returns a list of new version changes from a changelog."""

        changes = []

        for line in self.file_helper.iter_after(offset=self._offset_change):

            if not line.strip():
                break

            changes.append(line)

        return changes

    def get_version_summary(self) -> str:
        """Return version summary string."""

        return '\n'.join(self.get_changes()).strip()

    def sort_version_changes(self):
        """Sorts changes of the latest version inplace."""

        priorities = {prefix: priority for priority, prefix in enumerate(self.change_markers)}
        priority_default = 3

        def sorter(line):
            line = line.lower().replace('\'"`', '')
            priority = priorities.get(line[2], priority_default)
            return f'{priority} {line}'

        for line_offset, change in enumerate(sorted(self.get_changes(), key=sorter), 1):
            self.file_helper.line_replace(change, offset=line_offset)

    def write(self):
        self.sort_version_changes()
        super().write()


class Project:
    """Encapsulates application (project) related logic."""

    @classmethod
    def find_packages(cls, where: Path, *, prefer: str) -> list[Path]:

        candidate = where / prefer / '__init__.py'

        if candidate.exists():
            return [candidate.parent]

        packages_found = [
            obj
            for obj in where.iterdir()
            if obj.is_dir() and (obj / '__init__.py').exists() and 'tests' not in obj.name
        ]

        return packages_found

    def __init__(self, project_path: Path = None, *, log_level: int = None):
        """
        :param project_path: Application root (containing pyproject.toml) path.
        :param log_level: Logging level

        """
        self.configure_logging(log_level)

        project_path = project_path or os.getcwd()
        self.project_path = Path(project_path)
        self.package: PackageData | None = None
        self.changelog: ChangelogData | None = None
        self.vcs = VcsHelper.get(project_path)
        self.venv = VenvHelper(project_path)

    def configure_logging(self, verbosity_lvl: int = None, format: str = '%(message)s'):
        """Switches on logging at a given level.

        :param verbosity_lvl:
        :param format:

        """
        configure_logging(verbosity_lvl, logger=LOG, format=format)

    def _gather_data(self):
        """Gathers data relevant for project related functions."""

        if self.package or self.changelog:
            return

        with chdir(self.project_path):
            project_path = self.project_path

            LOG.debug(f'Gathering info from `{project_path}` directory ...')

            marker_file = 'pyproject.toml'

            if not os.path.isfile(marker_file):
                raise ProjectorExeption(f'No `{marker_file}` file found in the current directory.')

            self.vcs.check()

            parent_dirname = project_path.parent.name

            packages = self.find_packages(project_path, prefer=parent_dirname)
            if not packages:
                # src layout
                packages = self.find_packages(project_path / 'src', prefer=parent_dirname)

            LOG.debug(f'Found packages: {packages}')

            if not packages:
                raise ProjectorExeption('No package found.')

            package = packages[0]

            self.package = PackageData.get(package_path=package)
            self.changelog = ChangelogData.get()

    def pull(self):
        """Pulls changes from a remote repository"""
        with chdir(self.project_path):
            self.vcs.pull()

    def get_release_info(self, increment: str | None = None) -> tuple[str, str]:
        """Returns release info tuple as part of release preparation.
        
        :param increment: Version chunk to increment (major, minor, patch)
            If not set, will be deduced from changelog data.

        """
        self._gather_data()
        changelog = self.changelog

        increment = increment or changelog.deduce_version_increment()

        next_version = self.package.version_bump(increment)
        next_version_str = changelog.version_bump(next_version)

        version_summary = changelog.get_version_summary()

        return next_version_str, version_summary

    def release(self, next_version_str: str, version_summary: str):
        """Makes application package release.

        * Bumps version number
        * Adds changelog info
        * Tags VCS
        """
        self._gather_data()
        vcs = self.vcs

        with chdir(self.project_path):

            for info in (self.package, self.changelog):
                info.write()
                vcs.add(info.filepath)

            LOG.debug('Commit VCS changes ...')

            vcs.commit(f'Release {next_version_str}')

            vcs.add_tag(next_version_str, version_summary, overwrite=True)

    def add_change(self, descriptions: list[str] | tuple[str, ...] | str, *, stage_modified: bool = True):
        """Add a change description into changelog.

        :param descriptions: Single change description.
            Or multiple changes descriptions in list or tuple.

        :param stage_modified: Whether to stage modified files to commit.

        """
        self._gather_data()
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

            commit_message = f'{changelog.filename} updated'

            files_to_stage = [changelog.filepath]

            if stage_modified:
                files_to_stage.extend(self.vcs.get_modified())

                # Set a description as a commit message.
                commit_message = '\n'.join(
                    description.strip(changelog.change_markers)
                    for description in descriptions
                )

            self.vcs.add(files_to_stage)
            self.vcs.commit(commit_message.strip())

    def publish(self):
        """Uploads project data to remote VCS and Python Package Index server."""
        LOG.info('Publishing application ...')

        with chdir(self.project_path):
            self.vcs.push()
            DistHelper.upload()

    def style(self):
        LOG.info('Styling ...')
        Ruff.check()

    def docs(self, *, serve: bool = True):
        LOG.info('Making docs ...')
        MkDocs.serve() if serve else MkDocs.build()

    def venv_init(self, *, reset: bool = False, register_tool: bool = False):
        self.venv.initialize(reset=reset)

        register_tool and self.venv.register_tool()

    def tools_init(self, upgrade: bool = False):
        LOG.info(f'{"Upgrading" if upgrade else "Bootstrapping"} development tools ...')

        tools_default = [
            'tox',
            'ruff==0.13.1',
        ]

        method = Uv.tool_upgrade if upgrade else Uv.tool_install

        LOG.info(f'Processing uv ...')

        if upgrade:
            Uv.upgrade()
        else:
            Uv.install()

        for tool in tools_default:
            LOG.info(f'Processing {tool} ...')

            method(tool.partition('=')[0])
