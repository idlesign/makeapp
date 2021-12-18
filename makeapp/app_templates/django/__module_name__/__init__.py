{% extends parent_template %}

{% block body %}
{{ super() }}
default_app_config = '{{ module_name }}.apps.{{ module_name_capital }}Config'
{% endblock %}
