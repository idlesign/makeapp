#!/usr/bin/env python
"""
makeapp

Simplifies Python application rollout by providing its basic structure.

Can function both as a Python module and in command line mode
use `makeapp --help` command for information on available options.

"""
import os
import re
import sys
import logging
import argparse
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

try:
    input = raw_input
except NameError:
    pass

from contextlib import contextmanager
from subprocess import Popen
from datetime import date
from collections import OrderedDict

import requests

#TODO tests


RE_UNKNOWN_MARKER = re.compile(r'{{ [^}]+ }}')
PYTHON_VERSION = sys.version_info
BASE_PATH = os.path.dirname(__file__)


@contextmanager
def chdir(path):
    """Temporarily switches the current working directory.

    :param path:
    :return:
    """
    prev_wd = os.getcwd()
    os.chdir(path)
    yield
    os.chdir(prev_wd)


class AppMakerException(BaseException):
    """AppMaker exception."""


class AppMaker(object):
    """makeapp functionality is encapsulated in this class.

    Usage example:
        app_maker = AppMaker('my_app')
        app_maker.rollout('/home/idle/dev/my_app_env/')

    This will create `my_app` application skeleton in `/home/idle/dev/my_app_env/`.

    """

    user_data_path = os.path.join(os.path.expanduser('~'), '.makeapp')
    user_templates_path = os.path.join(user_data_path, 'app_templates')
    user_settings_config = os.path.join(user_data_path, 'makeapp.conf')

    default_templates_path = os.path.join(BASE_PATH, 'app_templates')
    default_template = '__default__'
    module_dir_marker = '__module_name__'

    license_templates_path = os.path.join(BASE_PATH, 'license_templates')
    LICENSE_NO = 'no'
    LICENSE_MIT = 'mit'
    LICENSE_APACHE = 'apache2'
    LICENSE_GPL2 = 'gpl2'
    LICENSE_GPL3 = 'gpl3'
    LICENSE_BSD2CL = 'bsd2cl'
    LICENSE_BSD3CL = 'bsd3cl'
    LICENSES = OrderedDict((
        (LICENSE_NO, ('No License', 'Other/Proprietary License')),
        (LICENSE_MIT, ('MIT License', 'OSI Approved :: MIT License')),
        (LICENSE_APACHE, ('Apache v2 License', 'OSI Approved :: Apache Software License')),
        (LICENSE_GPL2, ('GPL v2 License', 'OSI Approved :: GNU General Public License v2 (GPLv2)')),
        (LICENSE_GPL3, ('GPL v3 License', 'OSI Approved :: GNU General Public License v3 (GPLv3)')),
        (LICENSE_BSD2CL, ('BSD 2-Clause License', 'OSI Approved :: BSD License')),
        (LICENSE_BSD3CL, ('BSD 3-Clause License', 'OSI Approved :: BSD License')),
    ))
    default_license = LICENSE_BSD3CL

    VCS_GIT = 'git'
    VCS_HG = 'hg'
    VCS = OrderedDict((
        (VCS_GIT, 'Git'),
        (VCS_HG, 'Mercurial'),
    ))
    VCS_COMMANDS = {
        VCS_GIT: ('git init -q', 'git add -A .'),
        VCS_HG: ('hg init', 'hg add'),
    }
    default_vcs = VCS_GIT

    BASE_SETTINGS = OrderedDict((
        ('app_name', None),
        ('description', 'Sample short description'),
        ('author', '{{ app_name }} project contributors'),
        ('author_email', ''),
        ('url', 'https://pypi.python.org/pypi/{{ app_name }}'),
        ('year', str(date.today().year)),
        ('module_name', None),
        ('license', default_license),
        ('license_title', LICENSES[default_license][1]),
        ('license_title_pypi', LICENSES[default_license][1]),
        ('vcs', default_vcs),
        ('python_version', '.'.join(map(str, PYTHON_VERSION[:2]))),
        ('python_version_major', str(PYTHON_VERSION[0])),
    ))

    def __init__(self, app_name, templates_to_use=None, templates_path=None, log_level=None):
        """Initializes app maker object.

        :param app_name: Application name
        :param templates_to_use: Application names or paths to use for skeleton creation
        :param templates_path: A path where application skeleton templates reside
        :param log_level: Logging

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.configure_logging(log_level)

        if templates_path is None:
            if os.path.exists(self.user_templates_path):
                templates_path = self.user_templates_path
            else:
                templates_path = self.default_templates_path

        if not os.path.exists(templates_path):
            raise AppMakerException('Templates path doesn\'t exist: %s' % templates_path)
        self.templates_path = templates_path
        self.logger.debug('Templates path: %s' % self.templates_path)

        if templates_to_use is None:
            templates_to_use = []

        if not templates_to_use or self.default_template not in templates_to_use:
            templates_to_use.insert(0, self.default_template)

        self.use_templates = OrderedDict()
        for template in templates_to_use:
            name, path = self._find_template(template)
            self.use_templates[name] = path
        self.logger.debug('Templates to use: %s' % self.use_templates)

        self.settings = OrderedDict(self.BASE_SETTINGS)
        self.logger.debug('Initial settings: %s' % self.settings)

        self.update_settings({
            'app_name': app_name,
            'module_name': app_name.split('-', 1)[-1].replace('-', '_')
        })

    def _find_template(self, name_or_path):
        """Searches a template by it's name or in path.

        :param name_or_path:
        :return: A tuple (template_name, template_path)

        """
        supposed_paths = (
            name_or_path,
            os.path.join(self.templates_path, name_or_path),
            os.path.join(self.default_templates_path, name_or_path),
        )

        for supposed_path in supposed_paths:
            if '/' in supposed_path and os.path.exists(supposed_path):
                path = os.path.abspath(supposed_path)
                return path.split('/')[-1], path

        self.logger.error('Unable to find application template. Searched \n%s' % '\n  '.join(supposed_paths))
        raise AppMakerException('Unable to find application template: %s' % name_or_path)

    def _replace_settings_markers(self, target, strip_unknown=False):
        """Replaces settings markers in `target` with current settings values

        :param target:
        :param strip_unknown: Strip unknown markers from the target.
        :return: string

        """
        if target is not None:
            for name, val in self.settings.items():
                if val is not None:
                    target = target.replace('{{ %s }}' % name, val)
        if strip_unknown:
            target = re.sub(RE_UNKNOWN_MARKER, '', target)
        return target

    def check_app_name_is_available(self):
        """Check some sites whether an application name is not already in use.

        :return: boolean

        """
        self.logger.info('Checking `%s` name is available ...' % self.settings['app_name'])

        sites_registry = OrderedDict((
            ('Crate', 'https://crate.io/packages/{{ app_name }}/'),
            ('PyPI', 'https://pypi.python.org/pypi/{{ app_name }}'),
            ('Google Code', 'http://code.google.com/p/{{ app_name }}/')
        ))

        name_available = True

        for label, url in sites_registry.items():
            url = self._replace_settings_markers(url)
            response = requests.get(url)
            if response.status_code == 200:
                self.logger.warning('Application name seems to be in use: %s - %s' % (label, url))
                name_available = False
                break

        if name_available:
            self.logger.info('Application name `%s` seems to be available (no mention found at: %s)' % (self.settings['app_name'], ', '.join(sites_registry.keys())))

        return name_available

    def configure_logging(self, verbosity_lvl=None, format='%(message)s'):
        """Switches on logging at a given level.

        :param verbosity_lvl:
        :param format:

        """
        if not verbosity_lvl:
            verbosity_lvl = logging.INFO
        logging.basicConfig(format=format)
        self.logger.setLevel(verbosity_lvl)

    def _get_template_files(self):
        """Returns a dictionary containing all source files paths [gathered from different
        templates], indexed by relative paths.

        :return: dict

        """
        template_files = {}
        for name, templates_path in self.use_templates.items():
            for path, dirs, files in os.walk(templates_path):
                for fname in files:
                    full_path = os.path.join(path, fname)
                    rel_path = full_path.replace(self.module_dir_marker, self.settings['module_name']).replace(templates_path, '').lstrip('/')
                    template_files[rel_path] = full_path

        self.logger.debug('Template files: %s' % template_files.keys())
        return template_files

    def rollout(self, dest, overwrite=False, init_repository=False):
        """Rolls out the application skeleton into `dest` path.

        :param dest: app skeleton destination
        :param overwrite: boolean
        :param init_repository: boolean

        """
        self.logger.info('Application target path: %s' % dest)

        try:
            os.makedirs(dest)
        except OSError:
            pass

        if os.path.exists(dest) and overwrite:
            self.logger.warning('Target path already exists: %s. Conflict files will be overwritten.' % dest)

        license, license_src = self._get_license_data()
        license_src = self._comment_out(license_src)
        license_dest = os.path.join(dest, 'LICENSE')
        if not os.path.exists(license_dest) or overwrite:
            self._create_file(license_dest, license)

        files = self._get_template_files()
        for target, src in files.items():
            target = os.path.join(dest, target)
            if not os.path.exists(target) or overwrite:
                prepend = None
                if os.path.splitext(target)[1] == '.py':
                    # Prepend license text to source files if required.
                    prepend = license_src
                self._copy_file(src, target, prepend)

        if init_repository:
            self._vcs_init(dest, files.keys())

    @staticmethod
    def _comment_out(text):
        """Comments out (with #) the given data.

        :param text:

        """
        if text is None:
            return None
        return '#\n#%s\n' % text.replace('\n', '\n#')

    def _create_file(self, path, contents):
        """Creates a file with the given contents in the given path.
        Settings markers found in contents will be replaced with
        the appropriate settings values.

        :param path:
        :param contents:

        """
        contents = self._replace_settings_markers(contents, True)
        with open(path, 'w') as f:
            f.write(contents)

    def _copy_file(self, src, dest, prepend_data=None):
        """Copies a file from `src` to `dest` replacing settings markers
        with the given settings values, optionally prepending some data.

        :param src: source file
        :param dest: destination file
        :param prepend_data: data to prepend to dest file contents

        """
        self.logger.info('Creating %s ...' % dest)

        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(src) as f:
            data = f.read()

        if prepend_data is not None:
            data = prepend_data + data
        self._create_file(dest, data)

    def print_settings(self):
        """Print out settings dict, using logging mechanics."""
        self.logger.info('Settings: \n%s' % '\n'.join(['    %s: %s' % (k, v) for k, v in self.settings.items()]))
        self.logger.info('Chosen license: %s' % self.LICENSES[self.settings['license']][0])
        self.logger.info('Chosen VCS: %s' % self.VCS[self.settings['vcs']])

    def _get_license_data(self):
        """Returns license data: text, and boilerplate text
        to place into source files.

        :return: Tuple (license_text, license_src_text)
        """
        license_path = os.path.join(self.license_templates_path, self.settings['license'])

        if not os.path.exists(license_path):
            raise AppMakerException('Unable to find license file: %s' % license_path)

        with open(license_path) as f:
            license_text = f.read()

        license_src_text = None
        license_src_path = os.path.join(self.license_templates_path, '%s_src' % self.settings['license'])
        if os.path.exists(license_src_path):
            with open(license_src_path) as f:
                license_src_text = f.read()

        return license_text, license_src_text

    def update_settings_from_file(self, path=None):
        """Updates settings dict with contents of configuration file.

        Config example:

            [settings]
            author = Igor `idle sign` Starikov
            author_email = idlesign@yandex.ru
            license = mit
            url = https://github.com/idlesign/{{ app_name }}

        :param path: Config path. If empty default ~.makeapp config is used

        """
        config_path = path
        if path is None:
            config_path = self.user_settings_config

        if not os.path.exists(config_path) and path is not None:
            # Do not raise it for default config file.
            raise AppMakerException('Unable to find settings file: %s' % config_path)

        cfg = configparser.ConfigParser()
        cfg.read(config_path)

        if not cfg.has_section('settings'):
            raise AppMakerException('Unable to read settings from file: %s' % config_path)

        self.update_settings(dict(cfg.items('settings')))

    def _run_shell_command(self, command):
        """Runs the given shell command.

        :param command:
        :return: bool Status
        """
        self.logger.debug('Executing shell command: %s' % command)
        return not bool(Popen(command, shell=True).wait())

    def _vcs_init(self, dest, add_files=False):
        """Initializes an appropriate VCS repository in the given path.
        Optionally adds the given files.

        :param dest:
        :param add_files: boolean
        :return:
        """
        vcs = self.settings['vcs']
        self.logger.info('Initializing %s repository ...' % self.VCS[vcs])

        with chdir(dest):
            success = self._run_shell_command(self.VCS_COMMANDS[vcs][0])
            if success and add_files is not None:
                self._run_shell_command(self.VCS_COMMANDS[vcs][1])

    def _validate_setting(self, setting, variants):
        """Ensures that the given setting value is one from the given variants."""
        val = self.settings[setting]
        if val not in variants:
            raise AppMakerException('Unsupported value `%s` for `%s`. Acceptable variants [%s]' % (val, setting, variants))

    def update_settings(self, settings, verbose=False):
        """Updates current settings dictionary with values from a given
        settings dictionary. Settings markers existing in settings dict will
        be replaced with previously calculated settings values.

        :param settings:
        :param verbose: boolean, whether to log updated settings

        """
        self.settings.update(settings)
        for name, val in self.settings.items():
            self.settings[name] = self._replace_settings_markers(val)

        self._validate_setting('license', self.LICENSES.keys())
        self.settings['license_title'], self.settings['license_title_pypi'] = self.LICENSES[self.settings['license']]
        self.settings['python_version_major'] = self.settings['python_version'].split('.')[0]
        self._validate_setting('vcs', self.VCS.keys())


def main():

    argparser = argparse.ArgumentParser(prog='makeapp',
                                        description='Simplifies Python application rollout by providing its basic structure.')

    argparser.add_argument('app_name', help='Application name')
    argparser.add_argument('target_path', help='Path to create an application in')

    argparser.add_argument('--debug', help='Show debug messages while processing', action='store_true')

    # todo licenses dict behaves inappropriate
    flatten = lambda d: '; '.join(['%s - %s' % (k, v) for k, v in d.items()])  # Flattens a dictionary

    workflow_args_group = argparser.add_argument_group('Workflow options', 'These can be adjusted to customize the default makeapp behaviour')
    workflow_args_group.add_argument('-l', '--license', help='License to use: %s. [ Default: %s ]' % (flatten(AppMaker.LICENSES), AppMaker.default_license), choices=AppMaker.LICENSES.keys())
    workflow_args_group.add_argument('-vcs', '--vcs', help='VCS type to initialize a repo: %s. [ Default: %s ]' % (flatten(AppMaker.VCS), AppMaker.default_vcs), choices=AppMaker.VCS.keys())
    workflow_args_group.add_argument('-d', '--description', help='Short application description')
    workflow_args_group.add_argument('-f', '--configuration_file', help='Path to configuration file containing settings to read from')
    workflow_args_group.add_argument('-s', '--templates_source_path', help='Path containing application structure templates')
    workflow_args_group.add_argument('-t', '--templates_to_use', help='Accepts comma separated list of application structures templates names or paths')
    workflow_args_group.add_argument('-o', '--overwrite_on_conflict', help='Overwrite files on conflict', action='store_true')
    workflow_args_group.add_argument('-i', '--interactive', help='Ask for user input when decision is required', action='store_true')

    settings_args_group = argparser.add_argument_group('Customization', 'These basic settings can be adjusted to appropriate values one wants to see in application skeleton files')
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

