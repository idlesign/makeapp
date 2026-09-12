# Quickstart

This tutorial creates a project, runs its checks, builds its documentation, and records a change.

## Install makeapp

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first, then install `makeapp` as a tool:

```bash
uv tool install makeapp
ma --version
```

`ma` is an alias for `makeapp`.

## Create a project

```bash
ma new shiny_app ./shiny-app --description "My app" --author "I am" --no-prompt
cd shiny-app
```

`--no-prompt` skips the standard confirmation questions. It still initializes a Git repository and runs `uv sync` to
create `.venv`. Template-specific settings must be passed on the command line if a selected template requires them.

Without `--no-prompt`, `makeapp` can also:

- check whether the package name already exists on PyPI;
- let you skip Git or virtual environment initialization;
- configure a Git remote and optionally push the initial commit.

The default scaffold contains:

```text
shiny-app/
├── .github/workflows/python-package.yml
├── docs/
├── src/shiny_app/
├── tests/
├── CHANGELOG.md
├── LICENSE
├── README.md
├── mkdocs.yml
└── pyproject.toml
```

## Run the development workflow

Synchronize the environment after changing dependencies:

```bash
ma up
```

Run lint checks, tests, and a documentation build:

```bash
ma tools
ma style
ma tests
ma docs --build
```

`ma tools` installs the external Ruff command used by `ma style`. `ma docs --build` writes the site to `site/`; use
`ma docs` to start the local MkDocs server instead.

## Record a change

```bash
ma change "+ Add the first feature"
```

The command adds an entry under `Unreleased` in `CHANGELOG.md`, stages modified tracked files together with the
changelog, and creates a Git commit. See [Publishing](045_publishing.md) for change markers and the release workflow.

## Choose a template

Pass a comma-separated list to `-t` to extend the default scaffold:

```bash
ma new shiny_cli ./shiny-cli -t click --no-prompt
```

Later templates override files contributed by earlier templates. See [Bundled templates](030_skeletons.md) and
[Template authoring](025_template_authoring.md) for details.

## Shell completion

For Bash, add this line to `~/.bashrc`:

```bash
eval "$(_MAKEAPP_COMPLETE=bash_source makeapp)"
```
