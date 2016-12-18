#!/usr/bin/env python
"""
makeapp

Simplifies Python application rollout by providing its basic structure.

"""
import sys
import argparse
import logging

try:
    input = raw_input
except NameError:
    pass


from .appmaker import AppMaker


def main():

    argparser = argparse.ArgumentParser(
        prog='makeapp', description='Simplifies Python application rollout by providing its basic structure.')

    argparser.add_argument('app_name', help='Application name')
    argparser.add_argument('target_path', help='Path to create an application in')

    argparser.add_argument('--debug', help='Show debug messages while processing', action='store_true')

    workflow_args_group = argparser.add_argument_group(
        'Workflow options', 'These can be adjusted to customize the default makeapp behaviour')

    workflow_args_group.add_argument(
        '-l', '--license',
        help='License to use: %s. [ Default: %s ]' % (
            '; '.join(['%s - %s' % (k, v[0]) for k, v in AppMaker.LICENSES.items()]), AppMaker.default_license
        ),
        choices=AppMaker.LICENSES.keys())

    workflow_args_group.add_argument(
        '-vcs', '--vcs',
        help='VCS type to initialize a repo: %s. [ Default: %s ]' % (
            '; '.join(['%s - %s' % (k, v) for k, v in AppMaker.VCS.items()]), AppMaker.default_vcs
        ),
        choices=AppMaker.VCS.keys())

    workflow_args_group.add_argument(
        '-d', '--description',
        help='Short application description')

    workflow_args_group.add_argument(
        '-f', '--configuration_file',
        help='Path to configuration file containing settings to read from')

    workflow_args_group.add_argument(
        '-s', '--templates_source_path',
        help='Path containing application structure templates')

    workflow_args_group.add_argument(
        '-t', '--templates_to_use',
        help='Accepts comma separated list of application structures templates names or paths')

    workflow_args_group.add_argument(
        '-o', '--overwrite_on_conflict',
        help='Overwrite files on conflict', action='store_true')

    workflow_args_group.add_argument(
        '-i', '--interactive',
        help='Ask for user input when decision is required', action='store_true')

    settings_args_group = argparser.add_argument_group('Customization')
    base_settings_keys = AppMaker.BASE_SETTINGS.keys()
    for key in base_settings_keys:
        if key != 'app_name':
            try:
                settings_args_group.add_argument('--%s' % key)
            except argparse.ArgumentError:
                pass

    parsed = argparser.parse_args()

    app_maker_kwargs = {}
    if parsed.templates_source_path is not None:
        app_maker_kwargs['templates_path'] = parsed.templates_source_path

    if parsed.templates_to_use is not None:
        app_maker_kwargs['templates_to_use'] = parsed.templates_to_use.split(',')

    log_level = None
    if parsed.debug:
        log_level = logging.DEBUG

    app_maker = AppMaker(parsed.app_name, log_level=log_level, **app_maker_kwargs)

    # Try to read settings from default file.
    app_maker.update_settings_from_file()
    # Try to read settings from user supplied configuration file.
    app_maker.update_settings_from_file(parsed.configuration_file)

    # Settings from command line override all the previous.
    user_settings = {}
    for key in base_settings_keys:
        val = getattr(parsed, key, None)
        if val is not None:
            user_settings[key] = val

    def update_setting(settings):
        for setting in settings:
            val = getattr(parsed, setting, None)
            if val is not None:
                user_settings[setting] = val

    update_setting(('description', 'license', 'vcs'))

    app_maker.update_settings(user_settings)

    # Print out current settings.
    app_maker.print_settings()

    def process_input(prompt, variants=None):
        """Interprets user input.

        :param prompt:
        :param variants:
        :return: boolean
        """
        if not parsed.interactive:
            return True

        if variants is None:
            variants = ('Y', 'N')

        decision = input('%s [%s]: ' % (prompt, '/'.join(variants))).upper()
        if decision not in variants:
            return process_input(prompt)
        else:
            return decision == variants[0]

    if process_input('Do you want to check that the application name is not already in use?'):
        if not app_maker.check_app_name_is_available():
            sys.exit(1)

    if process_input('Ready to rollout the application skeleton. Proceed?'):
        init_repo = process_input('Do you want to initialize a VCS repository in the application directory?')
        app_maker.rollout(parsed.target_path, overwrite=parsed.overwrite_on_conflict, init_repository=init_repo)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
