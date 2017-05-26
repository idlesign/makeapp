{% extends "__default__/setup.py" %}

{% block entry_points %}
        'console_scripts': ['{{ module_name }} = {{ module_name }}.cli:main'],
{% endblock %}
