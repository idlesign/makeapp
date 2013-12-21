Quickstart
============


Make new application skeleton using interactive mode (`-i`)::

    ./makeapp.py my_new_app /home/idle/dev/my_new_app_env/ -i -d "My application." --author "idle sign"


This will create a decent application skeleton (setup.py, docs, tests, etc.) and initialize Git repository.


Get some help on command line switches::

    ./makeapp.py --help


Note: This software can function both as a command line tool and as a Python module.


Put some default settings into a config (not to mess with command line switches anymore):

1. Create ``.makeapp`` (dot is required) directory in your HOME directory;
2. In ``.makeapp`` directory create ``makeapp.conf`` configuration file with a similar contents::

    [settings]
    author = Igor `idle sign` Starikov
    author_email = idlesign@yandex.ru
    license = bsd3cl
    url = https://github.com/idlesign/{{ app_name }}
    vcs=git

