makeapp
=======
https://github.com/idlesign/makeapp

|release| |lic| |coverage|

.. |release| image:: https://img.shields.io/pypi/v/makeapp.svg
    :target: https://pypi.python.org/pypi/makeapp

.. |lic| image:: https://img.shields.io/pypi/l/makeapp.svg
    :target: https://pypi.python.org/pypi/makeapp

.. |coverage| image:: https://img.shields.io/coveralls/idlesign/makeapp/master.svg
    :target: https://coveralls.io/r/idlesign/makeapp


Description
------------

*Simplifies Python application rollout and publishing.*

* Make a skeleton for your new application with one console command.
* Automatically create a VCS repository for your application.
* Automatically check whether the chosen application name is not already in use.
* Customize new application layouts with skeleton templates.
* Put some skeleton default settings into a configuration file not to mess with command line switches anymore.
* Easily add entries to your changelog.
* Publish your application to remotes (VCS, PyPI) with single command.


Application scaffolding
-----------------------

Scaffold a new application:

.. code-block:: bash

    $ makeapp new my_new_app /home/librarian/mynewapp/ -d "My application." --author "The Librarian"


This will create a decent application skeleton using the default skeleton template (``setup.py``, docs, tests, etc.)
and initialize Git repository.

``makeapp`` also bundles templates for commonly used application types:

* ``click`` powered app
* ``pytest`` powered app
* ``pytest`` plugin
* ``Django`` app
* ``webscaff`` project (https://github.com/idlesign/webscaff)
* etc.

Multiple templates can be used together. Complete list of featured templates can be found in the documentation.
User-made templates are also supported.


Application publishing
----------------------

When you're ready to publish issue the following command while in project directory (containing ``setup.py``):

.. code-block:: bash

    $ makeapp release
    ; Bump version number part manually: major, minor, patch
    $ makeapp release --increment major


This will automatically:

* bump up application version number
* tag version in VCS
* push sources to remote repository
* upload application package to PyPI


Adding changes
--------------

When you're ready to add another entry to your changelog use ``change`` command:

.. code-block:: bash

    $ makeapp change "+ New 'change' command implemented"

This will also stage and commit all changed files.

Supported message prefixes:

* ``+`` - New feature / addition.

  Increments *minor* part of version number on ``release`` command.

* ``!`` - Important change/improvement/fix.

  Increment: *patch* part.

* ``-`` - Feature deprecation / removal

  Increment: *patch*.

* ``*`` - Minor change/improvement/fix. ``*`` prefix is added by default if none of the above mentioned prefixes found.

  Increment: *patch*.


Bash completion
---------------

To enable bash completion for ``makeapp`` command append the following line into your ``.bashrc``:

.. code-block:: bash

    eval "$(_MAKEAPP_COMPLETE=source makeapp)"


Documentation
-------------

https://makeapp.readthedocs.org/
