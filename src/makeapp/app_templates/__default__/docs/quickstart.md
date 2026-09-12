# Quickstart

Install {{ app_name }} in an existing uv project:

```bash
uv add {{ app_name }}
```

To work on the source checkout, synchronize dependencies and run the checks:

```bash
uv sync
uv run pytest
uv run mkdocs build --strict
```

Start the local documentation server with:

```bash
uv run mkdocs serve
```
