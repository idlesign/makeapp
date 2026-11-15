import re
import shutil

from ..exceptions import CommandError
from ..utils import run_command
from .vcs import VcsHelper

RE_GITHUB_URL = re.compile(r'github\.com[:/](?P<slug>[^\s]+?)(?:\.git)?$')


class GithubHelper:
    """Encapsulates GitHub related actions: releases and repository management."""

    def __init__(self, vcs_helper: VcsHelper):
        self.vcs = vcs_helper

    @classmethod
    def is_available(cls) -> bool:
        """Returns whether GitHub CLI (`gh`) is available."""
        return shutil.which('gh') is not None

    def get_repo_slug(self) -> str | None:
        """Returns repository slug (owner/repo) if origin points to GitHub."""
        try:
            url = self.vcs.run_command(['remote', 'get-url', 'origin'])[0]

        except (CommandError, IndexError):
            return None

        match = RE_GITHUB_URL.search(url)
        return match.group('slug') if match else None

    def get_latest_tag(self) -> str:
        """Returns the most recent tag."""
        return self.vcs.run_command(['describe', '--tags', '--abbrev=0'])[0]

    def create_release(self, tag: str = None) -> str:
        """Creates a GitHub release for a tag, using the tag annotation as release notes.
        Returns the release URL.

        :param tag: Tag to create a release for. The latest tag is used if not given.

        """
        tag = tag or self.get_latest_tag()

        output = run_command(['gh', 'release', 'create', tag, '--title', tag, '--notes-from-tag'])

        return output[0] if output else ''

    def create_repo(self, name: str, *, private: bool = True) -> str:
        """Creates a GitHub repository from the current directory and pushes it.
        Returns the repository URL.

        :param name: Repository name.
        :param private: Whether the repository is private.

        """
        visibility = '--private' if private else '--public'

        output = run_command(['gh', 'repo', 'create', name, visibility, '--source', '.', '--push'])

        return output[0] if output else ''

    def repo_exists(self, name: str) -> bool:
        """Returns whether a repository with the given name exists on GitHub.

        :param name: Repository name.

        """
        try:
            run_command(['gh', 'repo', 'view', name])

        except CommandError:
            return False

        return True

    def get_repo_url(self, name: str) -> str:
        """Returns SSH URL of an existing repository.

        :param name: Repository name.

        """
        return run_command(['gh', 'repo', 'view', name, '--json', 'sshUrl', '--jq', '.sshUrl'])[0]

    def link_repo(self, name: str):
        """Links an existing GitHub repository as origin and pushes to it.

        :param name: Repository name.

        """
        self.vcs.add_remote(self.get_repo_url(name))
        self.vcs.push(upstream=True)
