import io
import os
import re

from setuptools import setup, find_packages

{% block imports %}{% endblock %}

PATH_BASE = os.path.dirname(__file__)
{% block constants %}{% endblock %}


def read_file(fpath):
    """Reads a file within package directories."""
    with io.open(os.path.join(PATH_BASE, fpath)) as f:
        return f.read()


def get_version():
    """Returns version number, without module import (which can lead to ImportError
    if some dependencies are unavailable before install."""
    contents = read_file(os.path.join('{{ module_name }}', '__init__.py'))
    version = re.search('VERSION = \(([^)]+)\)', contents)
    version = version.group(1).replace(', ', '.').strip()
    return version


setup(
    name='{{ app_name }}',
    version=get_version(),
    url='{{ url }}',

    description='{{ description }}',
    long_description=read_file('README.rst'),
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

