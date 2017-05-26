import os
import io
from setuptools import setup, find_packages
{% block imports %}{% endblock %}

from {{ module_name }} import VERSION


PATH_BASE = os.path.dirname(__file__)
{% block constants %}{% endblock %}


def get_readme():
    # This will return README (including those with Unicode symbols).
    with io.open(os.path.join(PATH_BASE, 'README.rst')) as f:
        return f.read()


setup(
    name='{{ app_name }}',
    version='.'.join(map(str, VERSION)),
    url='{{ url }}',

    description='{{ description }}',
    long_description=get_readme(),
    license='{{ license_title }}',

    author='{{ author }}',
    author_email='{{ author_email }}',

    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,

    install_requires=[{% block install_requires %}{% endblock %}],
    setup_requires=[{% block setup_requires %}{% endblock %}],

    entry_points={
{% block entry_points %}
{% endblock %}
    },

{% block tests %}
    test_suite='tests',
{% endblock %}

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: {{ python_version_major }}',
        'Programming Language :: Python :: {{ python_version }}',
        'License :: {{ license_title_pypi }}'
    ],
)

