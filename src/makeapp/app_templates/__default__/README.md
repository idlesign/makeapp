# {{ app_name }}

[![PyPI - Version](https://img.shields.io/pypi/v/{{ app_name }})](https://pypi.org/project/{{ app_name }}/)
[![License](https://img.shields.io/pypi/l/{{ app_name }})](https://pypi.org/project/{{ app_name }}/)
[![Docs](https://img.shields.io/readthedocs/{{ app_name }})](https://{{ app_name }}.readthedocs.io/)
{% block badges %}
{% endblock %}

*{{ description }}*

Project homepage: <{{ url }}>

## Install

```bash
uv add {{ app_name }}
```

See [INSTALL.md](INSTALL.md) for installation from source and tool installation.

## Development

```bash
uv sync
uv run pytest
uv run mkdocs build --strict
```

Project documentation is available at <https://{{ app_name }}.readthedocs.io/>.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) before submitting an issue or pull request.
