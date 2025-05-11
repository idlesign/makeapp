{% extends parent_template %}

{% block entry_points %}{{ super() }}
        'console_scripts': ['{{ module_name }} = {{ module_name }}.manage:main'],
{% endblock %}

{% block tests %}
    tests_require=[
        'pytest',
        'pytest-djangoapp>=1.0.0',
    ],
{% endblock %}
