Quickstart
==========


Application scaffolding
-----------------------

Scaffold a new application:

.. code-block:: bash

    $ makeapp new my_new_app /home/librarian/mynewapp/ -d "My application." --author "The Librarian"


This will create a decent application skeleton (setup.py, docs, tests, etc.) and initialize Git repository.

Get some help on command line switches:

.. code-block:: bash

    $ makeapp --help


.. note:: This software can function both as a command line tool and as a Python module.


Settings in config
~~~~~~~~~~~~~~~~~~

Put some default settings into a config (not to mess with command line switches anymore):

1. Create ``.makeapp`` (dot is required) directory in your HOME directory;
2. In ``.makeapp`` directory create ``makeapp.conf`` configuration file with a similar contents::

    [settings]
    author = The Librarian
    author_email = librarian@discworld.wrld
    license = bsd3cl
    url = https://github.discworld.wrld/librarian/{{ app_name }}
    vcs = git


Settings in command line
~~~~~~~~~~~~~~~~~~~~~~~~

You can also pass settings values via command line options. Use ``--no-prompt`` switch to automate scaffolding:

.. code-block:: bash

    makeapp new my_new_app -t webscaff  --no-prompt --webscaff_domain "example.com" --webscaff_email "me@example.com" --webscaff_host "93.184.216.34" --vcs_remote "git@example.com:me/my_new_app.git"


Application publishing
----------------------

When you're ready to publish issue the following command while in project directory (containing setup.py):

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

When you're ready to add another entry to your changelog use `change` command:

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
