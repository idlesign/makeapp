Bundled application templates
=============================

``Makeapp`` comes with the following bundled application layout skeletons (templates):

.. note::

    You can mix application layout flavors with templates combinations.

    ``-t`` switch allows several comma-separated template names. Order matters.


Python module (simple application)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This template is used as a default (when no ``-t`` switch is given for ``makeapp`` command).

It acts as a **base one for other templates** in a sense that your application will have
all the files from i, yet they could be overwritten and more files added by other
templates.


Console application
~~~~~~~~~~~~~~~~~~~

Template alias: ``console``.

Use ``-t console`` command switch to rollout a console application skeleton.


Django application
~~~~~~~~~~~~~~~~~~

Template alias: ``django``.

Use ``-t django`` command switch to rollout a Django reusable application skeleton.


pytest support template
~~~~~~~~~~~~~~~~~~~~~~~

Template alias: ``pytest``.

Use ``-t pytest`` command switch to rollout Python application which will
use ``pytest`` instead of ``unittest`` for tests.


Click console application
~~~~~~~~~~~~~~~~~~~~~~~~~

Template alias: ``click``.

Use ``-t click`` command switch to rollout a console application which will use ``click`` instead of ``argparse``.


Webscaff project
~~~~~~~~~~~~~~~~

Template alias: ``webscaff``.

This template allows you to create a web-project (Django on uWSGI) structure almost ready for publishing
on VPS (cloud) services via Webscaff https://github.com/idlesign/webscaff

Use ``-t webscaff`` command switch to rollout Webscaff project.
