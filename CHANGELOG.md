# makeapp changelog


### Unreleased
* !! Big rewrite. Now uses up-to-date conventions and technologies.
* ++ Add 'ma' alias for 'makeapp' command.
* ++ Added virtual environment creation on project rollout.
* ++ CLI. Add 'publish' command.
* ++ CLI. Added 'venv reset' command.
* ++ CLI. Descriptions passed to 'change' command all go into a commit messages.
* ** Added QA for Py 3.11, 3.12, 3.13.
* ** Dropped QA for Py 3.7, 3.8, 3.9.
* ** Fixed package name availability check.


v1.9.1 [2023-05-19]
-------------------
* Added '-i' shortcut for '--increment' option of 'release' command.
* Fix license and vcs options handling for 'new' command (closes #5).


v1.9.0 [2023-01-21]
-------------------
+ App templates updated.
+ Dropped QA for Py 3.6.
+ Switched to 'twine' for package publishing.
* Switched to 'python3' binary.


v1.8.6 [2021-12-18]
-------------------
* Django app template fix for GitHub Actions config.


v1.8.5 [2021-12-18]
-------------------
* Django app template improved: added 4.0 QA; switched from Travis to GitHub Actions.
* Django. Template improved.


v1.8.4 [2021-05-23]
-------------------
* Webscaff. Switch to use a custom user model.


v1.8.3 [2021-05-22]
-------------------
* Webscaff. Updated to support Django 3.2 changes.


v1.8.2 [2021-04-20]
-------------------
* Django app template improved: added 3.2 QA.
* Now wheel package is checked only when required.


v1.8.1 [2021-01-15]
-------------------
* Webscaff. Update template.


v1.8.0 [2020-12-10]
-------------------
+ Added wheel module check.
+ CLI. Exception messages simplified.
+ Templates. Python 3.9 added to QA.
* Now aimed for Python 3+. Universal wheel build disabled.


v1.7.1 [2020-09-20]
-------------------
* Webscaff. Turn on HTTPS auto redirect.
* Webscaff. Update template.


v1.7.0 [2020-09-20]
-------------------
+ CLI. Allow setting 'vcs_remote' option.
* Django. Update template.
* Webscaff. Update template.


v1.6.1 [2020-05-19]
-------------------
* Django app template improved.


v1.6.0 [2020-05-07]
-------------------
+ CLI. Added '--no-prompt' option for 'new' command.
+ CLI. Print out target directory for 'new' command.
+ Introduced 'Config.cleanup' attribute to allow easy cleanups for templates.
* CLI. App name usage search in 'new' command now defaults to 'N'.
* Django reusable app template improved.


v1.5.2 [2020-05-06]
-------------------
* Fixed handling directories passed as template names.


v1.5.1 [2020-05-02]
-------------------
* Docs config extended with 'autodoc_mock_imports' hint.
* Docs theme reverted from alabaster to default.


v1.5.0 [2020-03-05]
-------------------
+ Added pytest plugin template.


v1.4.1 [2020-03-04]
-------------------
* Click. Fixed install_requires.


v1.4.0 [2020-02-17]
-------------------
! Dropped support for Python 2 and 3.5.
+ Django. Template updated. Tests now rely on pytest-djangoapp.
* Click. 'click' package set as required.
* Fixed 'tests' install as package.


v1.3.0 [2020-02-16]
-------------------
! Dropped QA for Python 2.
+ Changelogs now will contain version release dates.
+ Default template tox config now includes Py3.8 env.
+ Updated Sphinx files.
* Fixed 'VcsHelper.add_tag' on Py3.
* Improved 'webscaff' template.
* Now copying template file permissions to targets.


v1.2.0
------
+ Added experimental 'webscaff' project template.
+ Added support for configuration files in app templates.
* Django app template now for Django>=1.8 and Python>=3.5.
* Fixed multiple template inheritance.


v1.1.0
------
* Added QA for py3.7.
* Dropped QA for py<3.5.
* Template. Default. Python<3.4 removed from tox.
* Template. Django. Python<3.4 and  Django<1.8 removed from tox.
* Template. pytest. Empty init file from test directory.


v1.0.0
------
+ Celebrating 1.0.
+ CLI. 'change' command now accepts multiple changes descriptions.


v0.12.2
-------
* Django app template is updated.
* Improved multiple app templates handling.


v0.12.1
-------
* Fixed work of 'change' and 'release' commands for some builtin templates.
* Improved addition of a final dot into change description..


v0.12.0
-------
+ Added CONTRIBUTING file.
+ Changelog entries are sorter by priorities.
+ Final dot is automatically added to change description.
+ Introduced VERSION_STR constant.
+ setup.py now reads application version number w/o module import.
* 'Work in progress' note added into readme
* PyPI downloads badges removed


v0.11.1
-------
* 'new' command now won't commit files if not asked for this
* Fixed crash on commit message quotes


v0.11.0
-------
+ Added 'click' console application template.


v0.10.0
-------
* CLI: Fixed 'new' command crash if remote is given.
* CLI: 'release' now handles non-ASCII in changelog on Py2.
* Version number now starts with 0.0.0 Unreleased.
* CLI: pull on 'release' command now would not fail if no remote.
+ CommandError now handles non-ASCII.
+ CLI: 'new' command now asks whether to push files to remote.
+ Added suppport for non-ASCII symbols in template files.
* Fixed bogus rollout of all templates when none of them is specified.
* Python 3.6 added to tox configs.
* README badges inlined.


v0.9.1
------
* Fixed 'TypeError' on Python 3


v0.9.0
------
* Fixed template vars replacement for licenses.
+ Added get_app_title_rst() context function.
+ Templates now use Jinja inheritance.


v0.8.0
------
* CLI: Implemented 'change' command
* IMPORTANT: `click` and `jinja2` packages are now required.
* IMPORTANT: `makeapp` CLI now uses `new` command for skeleton rollouts.
* IMPORTANT: CLI now is interactive only.
+ CLI is now cross-platform.
+ New `apptools` module.
+ CLI: new `release` command.
+ Tests in projects now can be run using `python setup.py test`.
+ Default setup.py now handles readme with Unicode symbols.
+ Django app template now includes `config.py`.
+ Default app template now contains `setup.cfg`.
+ New `release` command for `setup.py` is now available.
+ Added `pytest` template switching test suite from `unittest` to `pytest`.
* Bytecode files from templates aren't copied anymore.
* Word `project` is removed from BSD 3 LICENSE
* Tox configs simplified.


v0.7.0
------
* Django app template updated with tests layout compatible with Django 1.7+
* Crate.io removed from search registry.
* Fixed exception when run w/o a user-defined config.
* Fixed --help message.


v0.6.0
------
+ Django app template updated for Django 1.7.
+ Added coveragerc files for default and Django templates
+ Added Travis CI config into Django app template.
* Improved mocking mechanism in Sphinx configuration.


v0.5.0
------
+ Default README updated with PyPI badge.
* Updated Django tox rules for Py3.
* Updated rst guide.


v0.4.0
------
+ Console application template updated.
+ ModuleMock boilerplate is added to docs' conf.py (can be used for http://readthedocs.org/)


v0.3.2
------
* `python_version_major` is now deduced from `python_version`
* From django app skeleton removed empty migrations dir.


v0.3.1
------
+ Added views.py into Django app template.
* Fixed interactive mode for py2.
* Fixed files discovery in bin/ (console apps).
* Removed bogus requests dependency from setup.py template.


v0.3.0
------
+ Added Django reusable app skeleton layout.
+ Now automatically creates a target dir hierarchy.
+ BSD 3 Clause license template is updated.


v0.2.0
------
+ Added console app skeleton layout.
+ Now can be aliased as /usr/local/bin/makeapp.


v0.1.0
------
+ Basic functionality.