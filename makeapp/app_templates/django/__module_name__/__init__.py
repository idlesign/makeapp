{% extends "__default__/__module_name__/__init__.py" %}

{% block body %}
{{ super() }}
default_app_config = '{{ module_name }}.config.{{ module_name_capital }}Config'
{% endblock %}

