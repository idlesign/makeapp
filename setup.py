import os
from setuptools import setup
from makeapp import VERSION

f = open(os.path.join(os.path.dirname(__file__), 'README.rst'))
README = f.read()
f.close()

setup(
    name='makeapp',
    version='.'.join(map(str, VERSION)),
    url='https://github.com/idlesign/makeapp',
    license='BSD',

    description='Simplifies Python application rollout by providing its basic structure.',
    long_description=README,

    author='Igor `idle sign` Starikov',
    author_email='idlesign@yandex.ru',

    packages=['makeapp'],
    include_package_data=True,
    zip_safe=False,

    install_requires=['requests'],
    scripts=['bin/makeapp'],

    classifiers=[
        # As in https://pypi.python.org/pypi?:action=list_classifiers
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
