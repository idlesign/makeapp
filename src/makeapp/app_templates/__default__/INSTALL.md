# Installing {{ app_name }}

Python {{ python_version }} or newer and [uv](https://docs.astral.sh/uv/) are required.

## From PyPI

Add the package to a project:

```bash
uv add {{ app_name }}
```

If the package exposes a command-line application, install it as an isolated tool:

```bash
uv tool install {{ app_name }}
```

Upgrade the tool with:

```bash
uv tool upgrade {{ app_name }}
```

## From source

Clone the repository and synchronize its development environment:

```bash
git clone https://example.com/owner/repository.git {{ app_name }}
cd {{ app_name }}
uv sync
```

Replace the example repository URL with the source repository. Run commands in the project environment with `uv run`.
