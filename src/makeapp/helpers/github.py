import re
import shutil

from ..exceptions import CommandError
from ..utils import run_command
from .vcs import VcsHelper

RE_GITHUB_URL = re.compile(r'github\.com[:/](?P<slug>[^\s]+?)(?:\.git)?$')


class GithubHelper:
    """Encapsulates GitHub Releases related actions."""

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
