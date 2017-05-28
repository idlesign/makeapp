Quickstart
==========


Application scaffolding
-----------------------

Bundled layout skeletons:

1. Python module (simple application);
2. Console application.
3. Django application.
4. Pytest support template.


Scaffold a new application:

.. code-block:: bash

    $ makeapp new my_new_app /home/librarian/mynewapp/ -d "My application." --author "The Librarian"


This will create a decent application skeleton (setup.py, docs, tests, etc.) and initialize Git repository.


Get some help on command line switches:

.. code-block:: bash

    $ makeapp --help


Note: This software can function both as a command line tool and as a Python module.


Put some default settings into a config (not to mess with command line switches anymore):

1. Create ``.makeapp`` (dot is required) directory in your HOME directory;
2. In ``.makeapp`` directory create ``makeapp.conf`` configuration file with a similar contents::

    [settings]
    author = The Librarian
    author_email = librarian@discworld.wrld
    license = bsd3cl
    url = https://github.discworld.wrld/librarian/{{ app_name }}
    vcs=git


Application publishing
----------------------

When you're ready to publish issue the following command while in project directory (containing setup.py):

.. code-block:: bash

    $ makeapp release


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


Bash completion
---------------

To enable bash completion for ``makeapp`` command append the following line into your ``.bashrc``:

.. code-block:: bash

    eval "$(_MAKEAPP_COMPLETE=source makeapp)"
