#!/usr/bin/env python
import sys
import logging

import click

from makeapp import VERSION
from makeapp.appmaker import AppMaker


TEMPLATE_VARS = AppMaker.BASE_SETTINGS.keys()


@click.group()
@click.version_option(version='.'.join(map(str, VERSION)))
def entry_point():
    """makeapp command line utilities."""


@entry_point.command()
@click.argument('app_name')
@click.argument('target_path')
@click.option('--debug', help='Show debug messages while processing', is_flag=True)
@click.option('--description', '-d', help='Short application description')
@click.option('--license', '-l',
              help='License to use',
              type=click.Choice(AppMaker.LICENSES.keys()),
              default=AppMaker.default_license)
@click.option('--vcs', '-vcs',
              help='VCS type to initialize a repo',
              type=click.Choice(AppMaker.VCS.keys()),
              default=AppMaker.default_vcs)
@click.option('--configuration_file', '-f',
              help='Path to configuration file containing settings to read from',
              type=click.Path(exists=True, dir_okay=False))
@click.option('--templates_source_path', '-s',
              help='Directory containing application structure templates',
              type=click.Path(exists=True, file_okay=False))
@click.option('--overwrite_on_conflict', '-o', help='Overwrite files on conflict', is_flag=True)
@click.option('--templates_to_use', '-t',
              help='Accepts comma separated list of application structures templates names or paths')
def new(app_name, target_path, configuration_file, overwrite_on_conflict, debug, **kwargs):
    """Simplifies Python application rollout providing its basic structure."""

    app_maker_kwargs = {
        'templates_path': kwargs['templates_source_path'],
        'templates_to_use': (kwargs['templates_to_use'] or '').split(',') or None,
    }

    log_level = None
    if debug:
        log_level = logging.DEBUG

    app_maker = AppMaker(app_name, log_level=log_level, **app_maker_kwargs)

    # Try to read settings from default file.
    app_maker.update_settings_from_file()
    # Try to read settings from user supplied configuration file.
    app_maker.update_settings_from_file(configuration_file)

    # Settings from command line override all the previous.
    user_settings = {}
    for key in TEMPLATE_VARS:
        val = kwargs.get(key)
        if val is not None:
            user_settings[key] = val

    app_maker.update_settings(user_settings)

    # Print out current settings.
    click.echo(click.style(app_maker.get_settings_string(), fg='green'))

    if click.confirm('Do you want to check that `%s` application name is not already in use?' % app_name, default=True):
        if not app_maker.check_app_name_is_available():
            sys.exit(1)

    click.confirm('Ready to rollout the application skeleton. Proceed?', abort=True)

    app_maker.rollout(
        target_path,
        overwrite=overwrite_on_conflict,
        init_repository=click.confirm('Do you want to initialize a VCS repository in the application directory?'))


def attach_template_vars():
    """Attaches command line options handlers to `new` command."""
    global new

    already_handled = ['app_name', 'description', 'license', 'vcs']

    for key in [key for key in TEMPLATE_VARS if key not in already_handled]:
        new = click.option('--%s' % key)(new)


def main():
    attach_template_vars()
    entry_point(obj={})


if __name__ == '__main__':
    main()
