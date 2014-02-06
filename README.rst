makeapp
=======
https://github.com/idlesign/makeapp


.. image:: https://pypip.in/d/makeapp/badge.png
        :target: https://crate.io/packages/makeapp


Description
------------

*Simplifies Python application rollout by providing its basic structure.*


* Make a skeleton for your new application with one console command.
* Automatically create a VCS repository for your application.
* Automatically check whether the chosen application name is not already in use.
* Customize new application layouts with `skeleton templates`.
* Put some skeleton default settings into a configuration file not to mess with command line switches anymore.


Bundled layout skeletons:

1. Python module (simple application);
2. Console application.
3. Django application.


Make new application skeleton using interactive mode (`-i`)::

    makeapp my_new_app /home/librarian/dev/my_new_app_env/ -i -d "My application." --author "The Librarian"


This will create a decent application skeleton (setup.py, docs, tests, etc.) and initialize Git repository.


Get some help on command line switches::

    makeapp --help


Note: This software can function both as a command line tool and as a Python module.


Put some default settings into a config not to mess with command line switches anymore:

1. Create ``.makeapp`` (dot is required) directory in your HOME directory;
2. In ``.makeapp`` directory create ``makeapp.conf`` configuration file with a similar contents::

    [settings]
    author = The Librarian
    author_email = librarian@discworld.wrld
    license = bsd3cl
    url = https://github.discworld.wrld/librarian/{{ app_name }}
    vcs=git



Documentation
-------------

http://makeapp.readthedocs.org/


.. image:: https://d2weczhvl823v0.cloudfront.net/idlesign/makeapp/trend.png
        :target: https://bitdeli.com/free
