#!/usr/bin/env python
import sys
import logging

import click

from makeapp import VERSION
from makeapp.appmaker import AppMaker
from makeapp.apptools import Project, VERSION_NUMBER_CHUNKS
from makeapp.utils import configure_logging


@click.group()
@click.version_option(version='.'.join(map(str, VERSION)))
def entry_point():
    """makeapp command line utilities."""


@entry_point.command(
    # Allow passing custom settings into app templates.
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.argument('app_name')
@click.argument('target_path')
@click.option(
    '--debug', is_flag=True,
    help='Show debug messages while processing')
@click.option(
    '-d', '--description',
    help='Short application description')
@click.option(
    '-l', '--license', type=click.Choice(AppMaker.LICENSES.keys()), default=AppMaker.default_license,
    help='License to use')
@click.option(
    '-vcs', '--vcs', type=click.Choice(AppMaker.VCS.keys()), default=AppMaker.default_vcs,
    help='VCS type to initialize a repo')
@click.option(
    '-f', '--configuration_file', type=click.Path(exists=True, dir_okay=False),
    help='Path to configuration file containing settings to read from')
@click.option(
    '-s', '--templates_source_path', type=click.Path(exists=True, file_okay=False),
    help='Directory containing application structure templates')
@click.option(
    '-o', '--overwrite_on_conflict', is_flag=True,
    help='Overwrite files on conflict')
@click.option(
    '-t', '--templates_to_use',
    help='Accepts comma separated list of application structures templates names or paths')
@click.argument('custom_args', nargs=-1, type=click.UNPROCESSED)
def new(app_name, target_path, configuration_file, overwrite_on_conflict, debug, custom_args, **kwargs):
    """Simplifies Python application rollout providing its basic structure."""

    def process_custom_args(args):
        processed = {}

        key = None

        for idx, arg in enumerate(args, 1):

            if idx % 2:

                if not arg.startswith('--'):
                    raise ValueError('Additional options should go in pairs: --opt val')

                key = arg.lstrip('-')

            else:
                processed[key] = arg

        return processed

    kwargs.update(process_custom_args(custom_args))

    app_maker_kwargs = {
        'templates_path': kwargs['templates_source_path'],
        'templates_to_use': (kwargs['templates_to_use'] or '').split(',') or None,
    }

    log_level = None
    if debug:
        log_level = logging.DEBUG

    app_maker = AppMaker(app_name, log_level=log_level, **app_maker_kwargs)

    app_maker.update_settings_complex(
        config=configuration_file,
        dictionary=kwargs,
    )

    # Print out current settings.
    click.secho(app_maker.get_settings_string(), fg='green')

    if click.confirm('Do you want to check that `%s` application name is not already in use?' % app_name, default=True):
        if not app_maker.check_app_name_is_available():
            sys.exit(1)

    click.confirm('Ready to rollout application skeleton. Proceed?', abort=True, default=True)

    init_repo = click.confirm('Do you want to initialize a VCS repository in the application directory?', default=True)

    remote_address = ''
    remote_push = False

    if init_repo:
        remote_address = click.prompt('Remote repository address to link to (leave blank to skip)', default='')

        if remote_address:
            remote_push = click.confirm('Do you want to commit and push files to remote?', default=False)

    app_maker.rollout(
        target_path,
        overwrite=overwrite_on_conflict,
        init_repository=init_repo,
        remote_address=remote_address,
        remote_push=remote_push,
    )


@entry_point.command()
@click.option('--increment', help='Version number chunk to increment', type=click.Choice(VERSION_NUMBER_CHUNKS))
@click.option('--debug', help='Show debug messages while processing', is_flag=True)
def release(increment, debug):
    """Performs new application version release."""

    if debug:
        configure_logging(logging.DEBUG)

    project = Project()

    project.pull()

    version_str, version_summary = project.get_release_info(increment)

    if not version_summary:
        click.secho('No changes found in changelog. Please add changes before release', fg='red', err=True)
        sys.exit(1)

    click.secho('Version current: %s' % project.package.version_current_str, fg='blue')
    click.secho('Version next: %s' % project.package.version_next_str, fg='green')
    click.secho(version_summary)

    if click.confirm('Commit changes?', default=True):
        project.release(version_str, version_summary)

        if click.confirm('Publish to remotes?', default=True):
            project.publish()


@entry_point.command()
@click.argument('description', nargs=-1)
def change(description):
    """Fixates a change adding a message to a changelog."""
    Project().add_change(description)


def main():
    entry_point(obj={})


if __name__ == '__main__':
    main()
