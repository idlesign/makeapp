Bundled application templates
=============================

``Makeapp`` comes with the following bundled application layout skeletons (templates):

* **Python module (simple application)**

  This template is used as a default (when no `-t` switch is given for `makeapp` command).

  It acts as a base one for other templates in a sense that your application will have
  all the files from i, yet they could be overwritten and more files added by other
  templates.

* **Console application**

  Template alias: ``console``. Use `-t console` command switch to rollout a console
  application skeleton.


* **Django application**

  Template alias: ``django``. Use `-t console` command switch to rollout a Django
  reusable application skeleton.



.. note::

    You can mix application layout flavors with templates combinations.

    `-t` switch allows several comma-separated template names. Order matters.

