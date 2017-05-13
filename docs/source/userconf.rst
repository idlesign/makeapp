User defined configuration
==========================

User defined configuration should be stored in ``.makeapp`` (dot is required) directory under user's HOME directory::

    /home/librarian/.makeapp/


Thus user can configure:

1. `makeapp` default settings, that are used on rollouts;
2. application layouts by providing skeleton templates.


.. note::

    User defined configuration is automatically loaded on every ``makeapp`` command call if not overrode
    by command line switches.



User defined settings
---------------------

Settings are read by `makeapp` from ``makeapp.conf`` file.

This is simply a configuration file::

    [settings]
    author = The Librarian
    author_email = librarian@discworld.wrld
    license = bsd3cl
    url = https://github.discworld.wrld/librarian/{{ app_name }}
    vcs=git
    year = 2010-2013


Such configuration simplifies application rollouts by making redundant command lines switches joggling, so::

    makeapp new my_new_app /home/librarian/dev/my_new_app_env/ -d "My application." --author "The Librarian" --year "2010-2013"

could be::

    makeapp new my_new_app /home/librarian/dev/my_new_app_env/ -d "My application."


.. note::

    You can also define different (and even your own settings) that are used in skeleton templates.



User defined application layouts
--------------------------------

User defined application layouts are searched in ``app_templates`` directory under ``.makeapp``.

Let's create a skeleton template named ``cool``:

1. Create ``cool`` directory::

  /home/librarian/.makeapp/app_templates/cool/

2. In ``cool`` directory create ``COOL.txt`` file with desired contents::

  echo "You'd better be cool." > /home/librarian/.makeapp/app_templates/cool/COOL.txt


Now you can use this skeleton template to rollout your application (`-t`)::

    makeapp new my_new_app /home/librarian/dev/my_new_app_env/ -d "My application." -t cool

After such a call you'll have an application default structure provided by `makeapp` extended with files
from ``cool``.


.. note::

    You can provide more application layout flavors by a combination of templates.

    `-t` switch allows several comma-separated template names. Order matters.
