# Local testing

`makeapp` comes with the ability to run tests (like `tox`, etc.) in different virtual environments:

!!! note
    * Static dependencies are taken from `tests` group of `dependency-groups` (from `pyproject.toml`).
    * Dynamic (varying environment) dependencies are taken from GitHub Actions workflow (see `strategy.matrix`).

## Tune tests

You may configure tests in `pyproject.toml`.

```toml
[tool.makeapp.tests]
workflow_github = "python-package.yml"  # This is the default (file from .github/workflows/), can be omitted.
deps = [
    # Additional dynamic dependencies are described here.
    "django~=${{ django-version }}.0",
]
```

## Run tests

```shell
ma tests
```

!!! note
    At the very beginning of the output all known environment are shown.

Use `--only` (`-o`) to run in certain environments:

```shell
ma tests -o "py314_django600" -o "py312_django520"
```
