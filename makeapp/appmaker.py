import logging
import os
import re
from collections import OrderedDict
from datetime import date

import requests

from .apptemplate import TemplateFile, AppTemplate
from .exceptions import AppMakerException
from .helpers.vcs import VcsHelper
from .rendering import Renderer
from .utils import chdir, configure_logging, PYTHON_VERSION, PY2

try:
    import configparser
except ImportError:
    import ConfigParser as configparser


RE_UNKNOWN_MARKER = re.compile(r'{{ [^}]+ }}')
BASE_PATH = os.path.dirname(__file__)


class AppMaker(object):
    """Scaffolding functionality is encapsulated in this class.

    Usage example:
        app_maker = AppMaker('my_app')
        app_maker.rollout('/home/idle/dev/my_app_env/')

    This will create `my_app` application skeleton in `/home/idle/dev/my_app_env/`.

    """
    template_default_name = '__default__'
    module_dir_marker = '__module_name__'

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

    VCS = VcsHelper.get_backends()

    default_vcs = list(VCS.keys())[0]

    BASE_SETTINGS = OrderedDict((
        ('app_name', None),
        ('module_name', None),
        ('description', 'Sample short description'),
        ('author', '{{ app_name }} contributors'),
        ('author_email', ''),
        ('url', 'https://pypi.python.org/pypi/{{ app_name }}'),
        ('year', str(date.today().year)),
        ('license', default_license),
        ('license_title', LICENSES[default_license][0]),
        ('vcs', default_vcs),
        ('python_version', '.'.join(map(str, PYTHON_VERSION[:2]))),
    ))

    app_template_default = None  # type: AppTemplate
    """Default (root) application template object. Populated at runtime."""

    def __init__(self, app_name, templates_to_use=None, templates_path=None, log_level=None):
        """Initializes app maker object.

        :param app_name: Application name
        :param templates_to_use: Application names or paths to use for skeleton creation
        :param templates_path: A path where application skeleton templates reside
        :param log_level: Logging

        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.configure_logging(log_level)

        self.path_user_confs = os.path.join(os.path.expanduser('~'), '.makeapp')
        self.path_templates_builtin = os.path.join(BASE_PATH, 'app_templates')
        self.path_templates_license = os.path.join(BASE_PATH, 'license_templates')

        self.user_settings_config = os.path.join(self.path_user_confs, 'makeapp.conf')
        self.path_templates_current = self._get_templates_path_current(templates_path)

        self.logger.debug('Templates path: %s', self.path_templates_current)

        self.app_templates = []
        self._init_app_templates(templates_to_use)

        self.settings = self._init_settings(app_name)

        self.renderer = Renderer(maker=self, paths=[
            self.path_templates_builtin,
            self.path_templates_current,
        ])

    def _init_settings(self, app_name):
        """Initializes and returns base settings.
        
        :param str|unicode app_name: 
        :rtype: OrderedDict 
        """

        settings = OrderedDict(self.BASE_SETTINGS)
        self.logger.debug('Initial settings: %s', settings)

        module_name = app_name.split('-', 1)[-1].replace('-', '_')

        self.update_settings({
            'app_name': app_name,
            'module_name': module_name,
            'vcs_remote': None,
        }, settings)

        return settings

    def _get_templates_path_current(self, path):
        """Returns current templates path.
        
        :param str|unicode|None path: 
        :rtype: str|unicode 
        """
        path_user_templates = os.path.join(self.path_user_confs, 'app_templates')

        if path is None:
            path = path_user_templates if os.path.exists(path_user_templates) else self.path_templates_builtin

        if not os.path.exists(path):
            raise AppMakerException("Templates path doesn't exist: %s" % path)

        return path

    def _init_app_templates(self, names_or_paths):
        """Returns a list of application template objects.
        
        :param list names_or_paths: 
        :rtype: list[AppTemplate]

        """
        if not names_or_paths:
            names_or_paths = []

        names_or_paths = [name for name in names_or_paths if name]

        default_template_name = self.template_default_name

        # Prepend default (base) template.
        if not names_or_paths or default_template_name not in names_or_paths:
            names_or_paths.insert(0, default_template_name)

        prev_template = None

        for template_spec in names_or_paths:

            prev_template = AppTemplate.contribute_to_maker(
                maker=self,
                template=template_spec,
                parent=prev_template,
            )

        self.logger.debug('Templates to use: %s', self.app_templates)

    def _replace_settings_markers(self, target, strip_unknown=False, settings=None):
        """Replaces settings markers in `target` with current settings values

        :param target:
        :param strip_unknown: Strip unknown markers from the target.
        :param OrderedDict settings:
        :rtype: str|unicode

        """
        settings = settings or self.settings

        if target is not None:
            for name, val in settings.items():
                if val is not None:
                    target = str(target).replace('{{ %s }}' % name, str(val))

        if strip_unknown:
            target = re.sub(RE_UNKNOWN_MARKER, '', target)

        return target

    def check_app_name_is_available(self):
        """Check some sites whether an application name is not already in use.

        :return: boolean

        """
        app_name = self.settings['app_name']

        self.logger.info('Checking `%s` name is available ...', app_name)

        sites_registry = OrderedDict((
            ('PyPI', 'https://pypi.python.org/pypi/' + app_name),
        ))

        name_available = True

        for label, url in sites_registry.items():
            response = requests.get(url)

            if response.status_code == 200:
                self.logger.warning('Application name seems to be in use: %s - %s', label, url)
                name_available = False
                break

        if name_available:
            self.logger.info(
                'Application name `%s` seems to be available (no mention found at: %s)',
                self.settings['app_name'], ', '.join(sites_registry.keys()))

        return name_available

    def configure_logging(self, verbosity_lvl=None, format='%(message)s'):
        """Switches on logging at a given level.

        :param verbosity_lvl:
        :param format:

        """
        configure_logging(verbosity_lvl, logger=self.logger, format=format)

    def _get_template_files(self):
        """Returns a dictionary containing all source files paths [gathered from different
        templates], indexed by relative paths.

        :return: OrderedDict

        """
        template_files = OrderedDict()

        for template in self.app_templates:
            template_files.update(template.get_files())

        self.logger.debug('Template files: %s', template_files.keys())

        return template_files

    def _hook_run(self, hook_name):
        """Runs the named hook for every app template.

        Returns results dictionary indexed by app template objects.

        :param str|unicode hook_name:
        :rtype: OrderedDict

        """
        results = OrderedDict()

        for app_template in self.app_templates:
            results[app_template] = app_template.run_config_hook(hook_name)

        return results

    def rollout(self, dest, overwrite=False, init_repository=False, remote_address=None, remote_push=False):
        """Rolls out the application skeleton into `dest` path.

        :param str|unicode dest: App skeleton destination path.

        :param bool overwrite: Whether to overwrite existing files.

        :param bool init_repository: Whether to initialize a repository.

        :param str|unicode remote_address: Remote repository address to add to DVCS.

        :param bool remote_push: Whether to push to remote.

        """
        self.logger.info('Application target path: %s', dest)

        # Make remote available for hooks.
        self.settings['vcs_remote'] = remote_address

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

        with chdir(dest):
            self._hook_run('rollout_pre')

        files = self._get_template_files()
        for target, template_file in files.items():
            target = os.path.join(dest, target)

            if not os.path.exists(target) or overwrite:

                prepend = None

                if os.path.splitext(target)[1] == '.py':
                    # Prepend license text to source files if required.
                    prepend = license_src

                self._copy_file(template_file, target, prepend)

        with chdir(dest):
            self._hook_run('rollout_post')

        if init_repository:
            self._vcs_init(
                dest,
                add_files=bool(files.keys()),
                remote_address=remote_address,
                remote_push=remote_push)

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
        if PY2:
            contents = contents.encode('utf8')

        with open(path, 'w') as f:
            f.write(contents)
            if contents.endswith('\n'):
                f.write('\n')

    def _copy_file(self, src, dest, prepend_data=None):
        """Copies a file from `src` to `dest` replacing settings markers
        with the given settings values, optionally prepending some data.

        :param str|unicode template_name: source file
        :param TemplateFile src: source file
        :param str|unicode dest: destination file
        :param str|unicode prepend_data: data to prepend to dest file contents

        """
        self.logger.info('Creating %s ...', dest)

        dirname = os.path.dirname(dest)

        if not os.path.exists(dirname):
            os.makedirs(dirname)

        data = self.renderer.render(src)

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
            'Chosen VCS: %s' % self.VCS[self.settings['vcs']].TITLE
        ]
        return '\n'.join(lines)

    def _get_license_data(self):
        """Returns license data: text, and boilerplate text
        to place into source files.

        :return: Tuple (license_text, license_src_text)

        """
        def render(filename):
            path = os.path.join(self.path_templates_license, filename)

            if os.path.exists(path):
                return self.renderer.render(path)

            return None

        license = self.settings['license']

        return render(license), render('%s_src' % license)

    def get_template_vars(self):
        """Returns known template variables.
        
        :rtype: list 
        """
        items = set(AppMaker.BASE_SETTINGS.keys())

        for app_template in self.app_templates:
            items.update(app_template.config.settings.keys())

        return items

    def update_settings_complex(self, config=None, dictionary=None):
        """Updates current settings using multiple sources,

        :param str|unicode config:
        :param dict dictionary:

        """
        # Try to read settings from default file.
        self.update_settings_from_file()

        # Try to read settings from user supplied configuration file.
        self.update_settings_from_file(config)

        # Settings from command line override all the previous.
        self.update_settings_from_dict(dictionary)

        # Add template specific files.
        self.update_settings_from_app_templates()

    def update_settings_from_app_templates(self):
        """Updates current settings using app templates."""
        self._hook_run('configure')

    def update_settings_from_dict(self, dict_):
        """Updates settings dict with contents from a given dict.
        
        :param dict dict_:

        """
        if not dict_:
            return

        settings = {}

        for key in self.get_template_vars():
            val = dict_.get(key)
            if val is not None:
                settings[key] = val

        self.update_settings(settings)

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

    def _vcs_init(self, dest, add_files=False, remote_address=None, remote_push=False):
        """Initializes an appropriate VCS repository in the given path.
        Optionally adds the given files.

        :param str|unicode dest: Path to initialize VCS repository.

        :param bool add_files: Whether to add files to commit automatically.

        :param str|unicode remote_address: Remote repository address to add to DVCS.

        :param bool remote_push: Whether to push to remote.

        """
        vcs = self.settings['vcs']

        helper = self.VCS[vcs]()  # type: VcsHelper

        self.logger.info('Initializing %s repository ...', helper.TITLE)

        with chdir(dest):
            helper.init()
            add_files and helper.add()

            # Linking to a remote.
            if remote_address:
                helper.add_remote(remote_address)
                if remote_push:
                    helper.commit('The beginning')
                    helper.push(upstream=True)

    def _validate_setting(self, setting, variants, settings):
        """Ensures that the given setting value is one from the given variants."""
        val = settings[setting]
        if val not in variants:
            raise AppMakerException(
                'Unsupported value `%s` for `%s`. Acceptable variants [%s]' % (val, setting, variants))

    def update_settings(self, settings_new, settings_base=None):
        """Updates current settings dictionary with values from a given
        settings dictionary. Settings markers existing in settings dict will
        be replaced with previously calculated settings values.

        :param dict settings_new:
        :param OrderedDict settings_base:
        
        """
        settings_base = settings_base or self.settings

        settings_base.update(settings_new)
        for name, val in settings_base.items():
            settings_base[name] = self._replace_settings_markers(val, settings=settings_base)

        self._validate_setting('license', self.LICENSES.keys(), settings_base)
        self._validate_setting('vcs', self.VCS.keys(), settings_base)
