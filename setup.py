import io
import os
import re
import sys

from setuptools import setup

PATH_BASE = os.path.dirname(__file__)


def read_file(fpath):
    """Reads a file within package directories."""
    with io.open(os.path.join(PATH_BASE, fpath)) as f:
        return f.read()


def get_version():
    """Returns version number, without module import (which can lead to ImportError
    if some dependencies are unavailable before install."""
    contents = read_file(os.path.join('makeapp', '__init__.py'))
    version = re.search('VERSION = \(([^)]+)\)', contents)
    version = version.group(1).replace(', ', '.').strip()
    return version


setup(
    name='makeapp',
    version=get_version(),
    url='https://github.com/idlesign/makeapp',
    license='BSD',

    description='Simplifies Python application rollout and publishing.',
    long_description=read_file('README.rst'),

    author='Igor `idle sign` Starikov',
    author_email='idlesign@yandex.ru',

    packages=['makeapp'],
    include_package_data=True,
    zip_safe=False,

    setup_requires=['pytest-runner'] if 'test' in sys.argv else [],
    tests_require=['pytest'],
    install_requires=[
        'requests',
        'click',
        'jinja2<3.0',
        'wheel',
    ],
    entry_points={
        'console_scripts': ['makeapp = makeapp.cli:main'],
    },

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)
