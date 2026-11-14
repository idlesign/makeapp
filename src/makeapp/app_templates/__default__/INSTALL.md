# Installing {{ app_name }}

[uv](https://docs.astral.sh/uv/) is recommended for installation, though plain `pip` works too.

{% block pypi %}
## From PyPI

Add the package to a project:

```bash
uv add {{ app_name }}
```

or with pip:

```bash
pip install {{ app_name }}
```
{% endblock %}

## From source

Clone the repository and synchronize its development environment:

```bash
git clone {{ url }} {{ app_name }}
cd {{ app_name }}
uv sync
```

Run commands in the project environment with `uv run`.
