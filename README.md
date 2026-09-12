# makeapp

[![PyPI - Version](https://img.shields.io/pypi/v/makeapp)](https://pypi.org/project/makeapp/)
[![License](https://img.shields.io/pypi/l/makeapp)](https://pypi.org/project/makeapp/)
[![Coverage](https://img.shields.io/coverallsCoverage/github/idlesign/makeapp)](https://coveralls.io/github/idlesign/makeapp)
[![Docs](https://img.shields.io/readthedocs/makeapp)](https://makeapp.readthedocs.io/)

`makeapp` scaffolds Python projects and provides one CLI for their common development tasks. It can create a project
from composable templates, initialize Git and a virtual environment, run a GitHub Actions test matrix locally, maintain
a changelog, and publish releases.

## Install

Python 3.11 or newer and [uv](https://docs.astral.sh/uv/getting-started/installation/) are required.

```bash
uv tool install makeapp
```

Both `makeapp` and its short alias `ma` invoke the same command.

## Quick start

```bash
ma new shiny_app ./shiny-app --description "My app" --author "I am" --no-prompt
cd shiny-app
ma tests
```

The default scaffold contains a `src`-layout package, tests, project metadata, a changelog, and MkDocs documentation.
The non-interactive command also initializes Git and runs `uv sync` to create `.venv`.

Bundled templates can extend the default scaffold:

- `console` for an `argparse` command-line application;
- `click` for a Click command-line application;
- `django` for a reusable Django application;
- `pytestplugin` for a pytest plugin;
- `webscaff` for a Linux-hosted Django/Webscaff project.

For example:

```bash
ma new shiny_cli ./shiny-cli -t click --no-prompt
```

## Project workflow

```bash
ma up              # Synchronize the development environment.
ma style           # Run Ruff checks and apply safe fixes.
ma tests           # Run the configured test matrix.
ma docs --build    # Build documentation without starting a server.
ma change "+ Add a feature"  # Update the changelog and commit modified files.
ma release         # Prepare a release and optionally publish it.
```

Review changes before running `ma change`: it stages and commits modified tracked files together with the changelog.

## Documentation

The full user and extension documentation is available at <https://makeapp.readthedocs.io/>.

- [Quickstart](https://makeapp.readthedocs.io/en/latest/quickstart/)
- [CLI reference](https://makeapp.readthedocs.io/en/latest/cli_reference/)
- [Template authoring](https://makeapp.readthedocs.io/en/latest/template_authoring/)
- [Publishing](https://makeapp.readthedocs.io/en/latest/publishing/)
Issues and feature requests are welcome in the [GitHub issue tracker](https://github.com/idlesign/makeapp/issues).
