{% extends parent_template %}



{% block install_requires %}{{ super() }}
        'pytest',
{% endblock %}


{% block entry_points %}{{ super() }}
        'pytest11': ['{{ module_name }} = {{ module_name }}.entry'],
{% endblock %}


{% block classifiers %}{{ super() }}
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
{% endblock %}
