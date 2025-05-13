{% extends parent_template %}

{% block body %}
{{ super() }}
default_app_config = '{{ package_name }}.apps.{{ package_name_capital }}Config'
{% endblock %}
