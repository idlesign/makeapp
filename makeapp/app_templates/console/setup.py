{% extends parent_template %}

{% block entry_points %}
        'console_scripts': ['{{ module_name }} = {{ module_name }}.cli:main'],
{% endblock %}
