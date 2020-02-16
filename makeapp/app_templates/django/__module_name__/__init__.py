{% extends parent_template %}

{% block body %}
{{ super() }}
default_app_config = '{{ module_name }}.config.{{ module_name_capital }}Config'
{% endblock %}
