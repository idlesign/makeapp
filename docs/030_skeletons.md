# Bundled templates

Every rollout starts with the default Python module scaffold. Templates passed to `-t` extend that scaffold; later
templates override files from earlier ones when they contribute the same relative path.

## Default Python module

The default scaffold is selected when `-t` is omitted. It provides:

- `pyproject.toml` with Hatchling and dependency groups;
- a `src`-layout Python package;
- pytest tests and a GitHub Actions workflow;
- README, installation, contributing, license, authors, and changelog files;
- MkDocs configuration and starter documentation.

```bash
ma new library ./library --no-prompt
```

## Console application

Alias: `console`.

Adds an `argparse`-based command-line module and a `project.scripts` entry:

```bash
ma new console-app ./console-app -t console --no-prompt
```

## Click application

Alias: `click`.

Extends `console`, replaces its command-line module with Click, and adds the Click dependency:

```bash
ma new click-app ./click-app -t click --no-prompt
```

## Django application

Alias: `django`.

Creates a reusable Django application package with models, views, management command directories, translations,
templates, and pytest-djangoapp tests:

```bash
ma new django-addon ./django-addon -t django --no-prompt
```

## pytest plugin

Alias: `pytestplugin`.

Adds a pytest entry point and starter plugin tests:

```bash
ma new pytest-helper ./pytest-helper -t pytestplugin --no-prompt
```

## Webscaff project

Alias: `webscaff`.

Creates a Django project prepared for deployment through [Webscaff](https://github.com/idlesign/webscaff). Pytest
support comes from the default scaffold; the project template runs Django project generation, dependency installation,
migrations, and database initialization during rollout.

```bash
ma new website ./website -t webscaff --no-prompt \
  --webscaff_domain example.com \
  --webscaff_email admin@example.com \
  --webscaff_host 203.0.113.10
```

!!! warning
    `webscaff` targets Linux. It executes POSIX shell commands and requires Python development headers, a compiler,
    OpenSSL, PCRE, and PostgreSQL development libraries. Install the packages printed by `makeapp` before rollout.

## Combining templates

Pass aliases as a comma-separated list:

```bash
ma new app ./app -t django,click
```

Order matters. The default scaffold is inserted automatically, and each selected template can also inject its own
parent templates. Inspect the resulting files and run the generated test suite after combining templates.
