Quickstart
==========


Make new application skeleton using interactive mode (`-i`)::

    makeapp my_new_app /home/librarian/dev/my_new_app_env/ -i -d "My application." --author "The Librarian"


This will create a decent application skeleton (setup.py, docs, tests, etc.) and initialize Git repository.


Get some help on command line switches::

    makeapp --help


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

