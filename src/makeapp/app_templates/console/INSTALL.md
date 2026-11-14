{% extends parent_template %}

{% block pypi %}
## From PyPI

Install the command-line application as an isolated tool:

```bash
uv tool install {{ app_name }}
```

Upgrade it with:

```bash
uv tool upgrade {{ app_name }}
```

or with pip:

```bash
pip install {{ app_name }}
```
{% endblock %}
