{% extends parent_template %}

{% block imports %}
import sys
{% endblock %}

{% block setup_requires %}{{ super() }}] + (['pytest-runner'] if 'test' in sys.argv else []) + [{% endblock %}

{% block tests %}
{{ super() }}
    tests_require=['pytest'],
{% endblock %}
