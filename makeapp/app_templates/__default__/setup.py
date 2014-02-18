import os
from setuptools import setup
from {{ module_name }} import VERSION


PATH_BASE = os.path.dirname(__file__)
PATH_BIN = os.path.join(PATH_BASE, 'bin')

SCRIPTS = None
if os.path.exists(PATH_BIN):
    SCRIPTS = [os.path.join('bin', f) for f in os.listdir(PATH_BIN) if os.path.join(PATH_BIN, f)]

f = open(os.path.join(PATH_BASE, 'README.rst'))
README = f.read()
f.close()

setup(
    name='{{ app_name }}',
    version='.'.join(map(str, VERSION)),
    url='{{ url }}',

    description='{{ description }}',
    long_description=README,
    license='{{ license_title }}',

    author='{{ author }}',
    author_email='{{ author_email }}',

    packages=['{{ module_name }}'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[],
    scripts=SCRIPTS,

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

