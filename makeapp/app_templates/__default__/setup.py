import os
from setuptools import setup
from {{ module_name }} import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
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
