# Developer tools

Project commands expect to run from the directory containing `pyproject.toml`. Use `--debug` on any command to display
the underlying external commands and additional diagnostic messages.

## Synchronize the environment

```bash
ma up
```

This runs `uv sync` and uses `.venv` as the project environment.

Use `--reset` to remove `.venv` before synchronization:

```bash
ma up --reset
```

If the project exposes a command through `project.scripts`, install the working tree as an editable uv tool:

```bash
ma up --tool
```

The options can be combined:

```bash
ma up --reset --tool
```

## Install development tools

```bash
ma tools
```

This installs shared Ruff. `ma tools --upgrade` updates uv and shared Ruff without changing project-specific versions.

## Run Ruff

```bash
ma style
```

The command runs `ruff check --fix`. It performs lint checks and applies available fixes; it does not run
`ruff format`.

If Ruff is a project dependency or `[tool.ruff].required-version` is set in `pyproject.toml`, `ma style` uses the
project's version. To upgrade it, update the requirement and lockfile when used, then run `ma style`.

## Build or serve documentation

Start the MkDocs development server and open it in a browser:

```bash
ma docs
```

Build the site into `site/` without starting a server:

```bash
ma docs --build
```

MkDocs and the configured theme must be present in the project environment. Projects created by the current default
template include them in the `docs` dependency group.

## Run tests

```bash
ma tests
```

See [Local testing](050_tests.md) for matrix configuration and environment selection.
