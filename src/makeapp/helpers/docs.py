import re
from pathlib import Path

import requests

RE_EXTERNAL_URL = re.compile(r'https?://[^\s)\]>"\'`]+')


class DocsHelper:
    """Encapsulates documentation related checks."""

    @classmethod
    def check_links(cls, docs_path: Path) -> list[str]:
        """Returns a list of dead external links found in Markdown files.

        :param docs_path: Documentation directory path.

        """
        problems = []

        for md_path in sorted(docs_path.rglob('*.md')):
            for line_num, line in enumerate(md_path.read_text(encoding='utf-8').splitlines(), 1):
                problems.extend(
                    f'{md_path}:{line_num}: {url}'
                    for url in cls.extract_urls(line)
                    if not cls.is_url_alive(url)
                )

        return problems

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """Extracts external URLs from a text."""
        return [url.rstrip('.,;:') for url in RE_EXTERNAL_URL.findall(text)]

    @staticmethod
    def is_url_alive(url: str) -> bool:
        """Checks whether the URL is reachable and responds with success."""
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)

            if response.status_code >= 400:
                # Some servers refuse HEAD requests.
                response = requests.get(url, allow_redirects=True, timeout=10, stream=True)

        except requests.RequestException:
            return False

        return response.status_code < 400
