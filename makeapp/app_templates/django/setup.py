{% extends parent_template %}

{% block tests %}
    tests_require=[
        'pytest',
        'pytest-djangoapp>=0.14.0',
    ],
{% endblock %}
