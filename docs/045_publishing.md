# Publishing

Makeapp uses `CHANGELOG.md`, the package `VERSION` constant, Git, and uv to prepare and publish releases.

## Prerequisites

Before releasing, verify that:

- the current directory contains `pyproject.toml` and `CHANGELOG.md`;
- exactly one import package can be identified, normally under `src/`;
- the package `__init__.py` contains a numeric `VERSION` with at least three components;
- Git is on a named branch and has a clean, reviewed working tree;
- the configured remote is reachable;
- tests and documentation pass;
- PyPI credentials are available to `uv publish`.

Set the token in the environment:

```bash
export UV_PUBLISH_TOKEN='pypi-...'
```

Alternatively, makeapp reads the `password` from the `pypi` section of `~/.pypirc` and passes it as
`UV_PUBLISH_TOKEN`:

```ini title="~/.pypirc"
[pypi]
password = pypi-...
```

## Record changes

```bash
ma change "+ Add JSON output"
```

`ma change` adds entries under `Unreleased`, stages modified tracked files together with the changelog, and creates a
commit. Multiple quoted descriptions can be passed in one invocation.

| Marker | Meaning | Automatic increment |
| --- | --- | --- |
| `+` | Feature or addition | Minor |
| `!` | Important change or fix | Patch |
| `-` | Deprecation or removal | Patch |
| `*` | Minor change or fix | Patch |

The marker is doubled in the stored changelog entry. When no supported marker is present, `*` is used. A final period is
added unless the description already ends with `.` or `!`.

## Prepare and publish a release

Run the project checks first:

```bash
ma style
ma tests
ma docs --build
ma release
```

`ma release` performs these steps:

1. pulls changes from the configured Git remote, if present;
2. calculates the next version from unreleased changelog entries;
3. displays the current version, next version, and release summary;
4. asks whether to update files, commit, and tag the version;
5. asks whether to push Git commits and tags and publish to PyPI.

A feature entry selects a minor increment; otherwise the default is patch. Override it explicitly when required:

```bash
ma release --increment major
```

Declining the first confirmation leaves version and changelog files unchanged. Declining publication keeps the local
release commit and tag so they can be reviewed before running `ma publish`.

## Publish an existing version

```bash
ma publish
```

This command does not change the version or create a tag. It pulls the repository, pushes the current branch and tags,
removes the existing `dist/` directory, runs `uv build`, and runs `uv publish`.
