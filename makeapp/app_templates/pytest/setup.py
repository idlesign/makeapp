import os
import io
import sys
from setuptools import setup, find_packages

from {{ module_name }} import VERSION


PATH_BASE = os.path.dirname(__file__)
PATH_BIN = os.path.join(PATH_BASE, 'bin')

SCRIPTS = None
if os.path.exists(PATH_BIN):
    SCRIPTS = [os.path.join('bin', f) for f in os.listdir(PATH_BIN) if os.path.join(PATH_BIN, f)]

PYTEST_RUNNER = ['pytest-runner'] if 'test' in sys.argv else []


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

    install_requires=[],
    setup_requires=[] + PYTEST_RUNNER,
    tests_require=['pytest'],

    scripts=SCRIPTS,

    test_suite='tests',

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
