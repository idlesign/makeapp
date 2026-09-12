# CLI reference

`makeapp` and `ma` are equivalent executables. Run commands from the project root unless the command creates a new
project.

```text
ma [COMMAND] --help
```

Every subcommand accepts `--debug` for additional diagnostic output.

## `ma new`

```text
ma new [OPTIONS] APP_NAME TARGET_PATH [CUSTOM_ARGS]...
```

Creates a project in `TARGET_PATH`. The default scaffold is always included.

| Option | Description |
| --- | --- |
| `-d`, `--description TEXT` | Set the short project description. |
| `-l`, `--license ALIAS` | Select `no`, `mit`, `apache2`, `gpl2`, `gpl3`, `bsd2cl`, or `bsd3cl`. |
| `-vcs`, `--vcs git` | Select the VCS implementation. |
| `-f`, `--configuration_file FILE` | Read rollout settings from an additional INI file. |
| `-s`, `--templates_source_path DIR` | Search for named templates in another directory. |
| `-o`, `--overwrite_on_conflict` | Replace existing destination files when paths conflict. |
| `--no-prompt` | Skip standard confirmation prompts. |
| `-t`, `--templates_to_use LIST` | Apply comma-separated template names or directory paths. |

Additional template settings use `--name value` pairs. For example:

```bash
ma new website ./website -t webscaff --no-prompt \
  --webscaff_domain example.com \
  --webscaff_email admin@example.com \
  --webscaff_host 203.0.113.10
```

In interactive mode, `ma new` can check the name on PyPI, initialize Git, configure a remote, push an initial commit,
and create `.venv`. With `--no-prompt`, Git and `.venv` initialization remain enabled, while name checking and the
initial remote push are skipped.

## `ma change`

```text
ma change [DESCRIPTION]...
```

Adds one or more descriptions to the `Unreleased` section of `CHANGELOG.md`, stages modified tracked files together
with the changelog, and commits them.

```bash
ma change "+ Add JSON output" "* Fix help text"
```

See [Publishing](045_publishing.md) for markers and version selection.

## `ma release`

```text
ma release [--increment major|minor|patch]
```

Pulls remote changes, calculates the next version, shows the release summary, and asks whether to commit and publish.
On commit it updates the package version and changelog, creates a release commit, and creates an annotated Git tag.
Publishing then pushes commits and tags, builds distributions, and uploads them to PyPI.

Without `--increment`, a `++` changelog entry selects a minor release and all other entries select a patch release.

## `ma publish`

```text
ma publish
```

Publishes the current version without changing version files or creating a tag. It pulls and pushes the Git repository,
pushes tags, runs `uv build`, and runs `uv publish`.

## `ma up`

```text
ma up [--reset] [--tool]
```

Runs `uv sync` for the current project.

- `-r`, `--reset` removes `.venv` before synchronization.
- `-t`, `--tool` additionally installs the current project as a forced editable uv tool.

## `ma tools`

```text
ma tools [--upgrade]
```

Installs Ruff. `-u` or `--upgrade` updates uv and reinstalls the configured tools.

## `ma style`

Runs `ruff check --fix`. This checks code and applies available fixes, but does not run `ruff format`.

## `ma tests`

Runs the GitHub Actions matrix configured for the project. Repeat `-o` or `--only` to select environment identifiers:

```bash
ma tests -o py314_django600 -o py312_django520
```

See [Local testing](050_tests.md) for matrix configuration and environment selection.

## `ma docs`

Starts `mkdocs serve -o` by default. Use `-b` or `--build` to run `mkdocs build` without starting a server:

```bash
ma docs --build
```
