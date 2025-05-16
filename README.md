# makeapp

https://github.com/idlesign/makeapp

[![PyPI - Version](https://img.shields.io/pypi/v/makeapp)](https://pypi.python.org/pypi/makeapp)
[![License](https://img.shields.io/pypi/l/makeapp)](https://pypi.python.org/pypi/makeapp)
[![Coverage](https://img.shields.io/coverallsCoverage/github/idlesign/makeapp)](https://coveralls.io/r/idlesign/makeapp)
[![Docs](https://img.shields.io/readthedocs/makeapp)](https://makeapp.readthedocs.io/)

## Description

*Simplifies Python application rollout and publishing.*

* Make a skeleton for your new application with one console command.
* Automatically create a VCS repository for your application.
* Automatically check whether the chosen application name is not already in use.
* Customize new application layouts with skeleton templates.
* Put some skeleton default settings into a configuration file not to mess with command line switches anymore.
* Easily add entries to your changelog.
* Publish your application to remotes (VCS, PyPI) with single command.


## Application scaffolding

Scaffold a new application:

``` bash
ma new shiny_app /home/librarian/shiny/ --description "My app." --author "I am"
```

!!! note
    `ma` is a convenient alias for `makeapp` command.

This will create a decent application skeleton using the default skeleton template (``pyproject.toml``, docs, tests, etc.)
and initialize Git repository.

`makeapp` also bundles templates for commonly used application types:

* `click` powered app
* `pytest` plugin
* `Django` app
* `webscaff` project [here](https://github.com/idlesign/webscaff)
* etc.

Multiple templates can be used together. Complete list of featured templates can be found in the documentation.
User-made templates are also supported.


## Adding changes

When you're ready to add another entry to your changelog use `change` command:

``` bash
ma change "+ New 'change' command implemented"
```

This will also stage and commit all changed files.

## Application publishing

When you're ready to publish issue the following command:

``` bash
ma release
; Bump version number part manually: major, minor, patch
ma release --increment major
```

This will automatically:

* bump up application version number
* tag version in VCS
* push sources to remote repository
* upload application package to PyPI

## Documentation

https://makeapp.readthedocs.io/
