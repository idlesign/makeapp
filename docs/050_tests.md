# Local testing

`ma tests` reuses the strategy matrix from a GitHub Actions workflow to execute the test suite in multiple uv-managed
environments. It is intended as a lightweight local alternative to duplicating that matrix in tox configuration.

## Dependency sources

- Static test dependencies come from the `tests` dependency group in `pyproject.toml`.
- Matrix dimensions and exclusions come from `strategy.matrix` in the selected GitHub Actions workflow.
- Additional dependencies that vary with matrix values come from `[tool.makeapp.tests].deps`.

By default, the workflow is `.github/workflows/python-package.yml`.

## Configure dynamic dependencies

```toml
[tool.makeapp.tests]
workflow_github = "python-package.yml"
deps = [
    "django~=${{ django-version }}.0",
]
```

`${{ django-version }}` is replaced with the value from the current matrix combination. The `python-version` matrix
value selects the interpreter passed to `uv sync`; when it is absent, makeapp uses the running Python version.

An absolute or relative workflow path can also be supplied. A filename without directories is resolved under
`.github/workflows/`.

## Run the matrix

```bash
ma tests
```

Before executing tests, makeapp prints all discovered matrix combinations. When exactly one combination remains after
applying the optional `--only` filter, makeapp reuses the project `.venv` if its Python major and minor version match
the combination's `python-version`. Static test dependencies are synchronized with `--group tests`, and resolved
dynamic dependencies are temporarily added with `--with` in the same `uv run` invocation.

When multiple combinations are selected, `.venv` is missing, or its Python version does not match, each combination
receives an isolated environment under `.venv_ma/`, then runs:

1. `uv sync --only-group tests --python <version>`;
2. `uv pip install` for resolved dynamic dependencies, when configured;
3. `uv run pytest`.

## Select environments

Use `--only` or `-o` one or more times:

```bash
ma tests -o py314_django600 -o py312_django520
```

Identifiers start with `py<version>` and append each resolved dynamic dependency. Punctuation is removed, so
`django~=6.0` becomes `django600`. Copy identifiers from the matrix list printed by `ma tests` rather than constructing
them manually.

## Cleanup

The isolated environments are reusable and remain in `.venv_ma/`. Remove that directory when you need to recreate
every matrix environment from scratch.
