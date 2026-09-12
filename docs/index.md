# Introduction

`makeapp` scaffolds Python projects and provides one command-line interface for routine development tasks.

It can:

- create a `src`-layout Python project from composable templates;
- initialize Git and a uv-managed virtual environment;
- maintain a changelog and calculate the next release version;
- run a GitHub Actions test matrix locally;
- run Ruff checks and build MkDocs documentation;
- push Git tags and publish distributions to PyPI.

## Requirements

- Python 3.11 or newer;
- [uv](https://docs.astral.sh/uv/getting-started/installation/);
- Git for repository and release commands.

Some templates have additional requirements. In particular, `webscaff` targets Linux and requires system development
packages described on the [bundled templates](030_skeletons.md) page.

## Installation

```bash
uv tool install makeapp
```

Upgrade an existing installation with:

```bash
uv tool upgrade makeapp
```

The `makeapp` executable also has the `ma` alias. All examples in this documentation use the shorter form.

## Where to start

1. Follow the [quickstart](010_quickstart.md) to create and validate a project.
2. Consult the [CLI reference](015_cli_reference.md) for commands and side effects.
3. Read about [configuration](020_userconf.md) and [bundled templates](030_skeletons.md).
4. Use the [template authoring guide](025_template_authoring.md) to create a custom layout.
5. Read the [publishing guide](045_publishing.md) before the first release.

## Project links

- [Source code](https://github.com/idlesign/makeapp)
- [Issue tracker](https://github.com/idlesign/makeapp/issues)
- [PyPI](https://pypi.org/project/makeapp/)
