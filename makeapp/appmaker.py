import os
import re
import sys
import logging
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
from contextlib import contextmanager
from subprocess import Popen
from datetime import date
from collections import OrderedDict

import requests

from .helpers.vcs import VcsHelper
from .exceptions import AppMakerException


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
    VCS_COMMANDS = {  # todo switch to VcsHelper
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
        self.logger.debug('Templates path: %s', self.templates_path)

        if templates_to_use is None:
            templates_to_use = []

        if not templates_to_use or self.default_template not in templates_to_use:
            templates_to_use.insert(0, self.default_template)

        self.use_templates = OrderedDict()
        for template in templates_to_use:
            name, path = self._find_template(template)
            self.use_templates[name] = path
        self.logger.debug('Templates to use: %s', self.use_templates)

        self.settings = OrderedDict(self.BASE_SETTINGS)
        self.logger.debug('Initial settings: %s', self.settings)

        module_name = app_name.split('-', 1)[-1].replace('-', '_')

        self.update_settings({
            'app_name': app_name,
            'module_name': module_name,
            'module_name_capital': module_name.capitalize(),
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

        self.logger.error('Unable to find application template. Searched \n%s', '\n  '.join(supposed_paths))
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
        self.logger.info('Checking `%s` name is available ...', self.settings['app_name'])

        sites_registry = OrderedDict((
            ('PyPI', 'https://pypi.python.org/pypi/{{ app_name }}'),
        ))

        name_available = True

        for label, url in sites_registry.items():
            url = self._replace_settings_markers(url)
            response = requests.get(url)
            if response.status_code == 200:
                self.logger.warning('Application name seems to be in use: %s - %s', label, url)
                name_available = False
                break

        if name_available:
            self.logger.info(
                'Application name `%s` seems to be available (no mention found at: %s)',
                self.settings['app_name'],
                ', '.join(sites_registry.keys())
            )

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
        for _, templates_path in self.use_templates.items():
            for path, _, files in os.walk(templates_path):
                for fname in files:

                    if fname == '__pycache__' or os.path.splitext(fname)[-1] == '.pyc':
                        continue

                    full_path = os.path.join(path, fname)
                    rel_path = full_path.replace(
                        self.module_dir_marker, self.settings['module_name']
                    ).replace(
                        templates_path, ''
                    ).lstrip('/')
                    template_files[rel_path] = full_path

        self.logger.debug('Template files: %s', template_files.keys())
        return template_files

    def rollout(self, dest, overwrite=False, init_repository=False, remote_address=None):
        """Rolls out the application skeleton into `dest` path.

        :param str|unicode dest: app skeleton destination
        :param bool overwrite:
        :param bool init_repository:
        :param str|unicode remote_address:
        """
        self.logger.info('Application target path: %s', dest)

        try:
            os.makedirs(dest)
        except OSError:
            pass

        if os.path.exists(dest) and overwrite:
            self.logger.warning('Target path already exists: %s. Conflict files will be overwritten.', dest)

        license_txt, license_src = self._get_license_data()
        license_src = self._comment_out(license_src)
        license_dest = os.path.join(dest, 'LICENSE')
        if not os.path.exists(license_dest) or overwrite:
            self._create_file(license_dest, license_txt)

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
            self._vcs_init(dest, bool(files.keys()), remote_address=remote_address)

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
        self.logger.info('Creating %s ...', dest)

        dirname = os.path.dirname(dest)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        with open(src) as f:
            data = f.read()

        if prepend_data is not None:
            data = prepend_data + data
        self._create_file(dest, data)

    def get_settings_string(self):
        """Returns settings string."""
        lines = [
            'Settings to be used: \n%s' % '\n'.join(
                ['    %s: %s' % (k, v) for k, v in sorted(self.settings.items(), key=lambda kv: kv[0])]
            ),
            'Chosen license: %s' % self.LICENSES[self.settings['license']][0],
            'Chosen VCS: %s' % self.VCS[self.settings['vcs']]
        ]
        return '\n'.join(lines)

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

        config_exists = os.path.exists(config_path)
        if path is None and not config_exists:
            # There could be no default config file.
            return

        if not config_exists and path is not None:
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
        self.logger.debug('Executing shell command: %s', command)
        return not bool(Popen(command, shell=True).wait())

    def _vcs_init(self, dest, add_files=False, remote_address=None):
        """Initializes an appropriate VCS repository in the given path.
        Optionally adds the given files.

        :param str|unicode dest:
        :param bool add_files:
        :param str|unicode remote_address:
        """
        vcs = self.settings['vcs']
        self.logger.info('Initializing %s repository ...', self.VCS[vcs])

        with chdir(dest):
            success = self._run_shell_command(self.VCS_COMMANDS[vcs][0])
            if success and add_files is not None:
                self._run_shell_command(self.VCS_COMMANDS[vcs][1])

        # Linking to a remote.
        if remote_address:
            # todo HG compatibility
            helper = VcsHelper.get(dest)
            helper.commit('The beginning')  # todo commit all?
            helper.add_remote(remote_address)
            helper.push(upstream=True if vcs == self.VCS_GIT else remote_address)

    def _validate_setting(self, setting, variants):
        """Ensures that the given setting value is one from the given variants."""
        val = self.settings[setting]
        if val not in variants:
            raise AppMakerException(
                'Unsupported value `%s` for `%s`. Acceptable variants [%s]' % (val, setting, variants)
            )

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
