import os
from collections import OrderedDict

from .exceptions import AppMakerException
from .utils import PYTHON_VERSION
from .appconfig import Config

if False:  # pragma: nocover
    from .appmaker import AppMaker


class AppTemplate(object):
    """Represents an application template."""

    config_filename = 'makeappconf.py'
    config_attr = 'makeapp_config'

    def __init__(self, maker, name, path, parent=None):
        """

        :param AppMaker maker:
        :param str name:
        :param str path:
        :param AppTemplate parent:

        """
        self.maker = maker
        self.name = name
        self.path = path
        self.parent = parent
        self.config = self._read_config()
        self._process_config()

    def __str__(self):
        return '%s: %s' % (self.name, self.path)

    @property
    def is_default(self):
        """Whether current template is default (root)."""
        return self.name == self.maker.template_default_name

    def _read_config(self):
        """Reads template's config.

        If not found, dummy config object is returned.

        :rtype: Config

        """
        module_fake_name = 'makeapp.config.%s' % self.name
        config_path = os.path.join(self.path, self.config_filename)

        if os.path.exists(config_path):

            if PYTHON_VERSION[0] == 2:
                import imp
                module = imp.load_source(module_fake_name, config_path)

            else:
                import importlib.util

                spec = importlib.util.spec_from_file_location(module_fake_name, config_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

            config = getattr(module, self.config_attr, None)  # type: type(Config)

            if not issubclass(config, Config):
                raise AppMakerException(
                    'Unable to load config class for "%" template. '
                    'Make sure "%s" file has "%s" attribute having value of AppConfig heir.')

            return config(app_template=self)

        return Config(app_template=self)

    def _process_config(self):
        parent_names = self.config.parent_template

        if parent_names:

            parent = self.parent

            for parent_name in parent_names:
                # Inject parents.
                # Here actually may be a graph, but
                # for now don't bother with it, just handle the simplest case.
                app_template = self.contribute_to_maker(
                    maker=self.maker,
                    template=parent_name,
                    parent=parent,
                )
                parent = app_template
                self.parent = app_template

    def run_config_hook(self, hook_name):
        """Runs a hook function from app config template if defined there.
        Returns `True` if a hook has been run.

        :param hook_name:
        :rtype: bool

        """
        hook_name = 'hook_%s' % hook_name
        hook_func = getattr(self.config, hook_name, None)

        if hook_func:
            hook_func()
            return True

        return False

    def get_files(self):
        """Returns a mapping of relative filenames to TemplateFiles objects.

        :rtype: OrderedDict

        """
        template_files = OrderedDict()

        maker = self.maker
        templates_path = self.path
        config_filename = self.config_filename

        for path, _, files in os.walk(templates_path):

            for fname in files:

                if fname == '__pycache__' or os.path.splitext(fname)[-1] == '.pyc' or fname == config_filename:
                    continue

                full_path = os.path.join(path, fname)

                rel_path = full_path.replace(templates_path, '').lstrip('/')

                template_file = TemplateFile(
                    template=self,
                    path_full=full_path,
                    path_rel=rel_path,
                )

                rel_path = rel_path.replace(maker.module_dir_marker, maker.settings['module_name'])
                template_files[rel_path] = template_file

        return template_files

    @classmethod
    def contribute_to_maker(cls, maker, template, parent):
        """
        :param AppMaker maker:
        :param str template:
        :param AppTemplate parent:
        :rtype: AppTemplate

        """
        name, path = cls._find(
            template,
            search_paths=(
                template,
                os.path.join(maker.path_templates_current, template),
                os.path.join(maker.path_templates_builtin, template),
            )
        )

        app_template = AppTemplate(
            maker=maker,
            name=name,
            path=path,
            parent=parent,
        )

        maker.app_templates.append(app_template)

        if app_template.is_default:
            maker.app_template_default = app_template

        return app_template

    @classmethod
    def _find(cls, name_or_path, search_paths):
        """Searches a template by it's name or in path.

        :param name_or_path:
        :return: A tuple (template_name, template_path)
        :param tuple search_paths:
        :rtype: tuple[str, str]

        """
        for supposed_path in search_paths:
            if '/' in supposed_path and os.path.exists(supposed_path):
                path = os.path.abspath(supposed_path)
                return path.split('/')[-1], path

        raise AppMakerException(
            'Unable to find application template %s. Searched \n%s' % (name_or_path, '\n  '.join(search_paths)))


class TemplateFile(object):
    """Represents app template file info."""

    __slots__ = ['template', 'path_full', 'path_rel']

    def __init__(self, template, path_full, path_rel):
        """
        :param AppTemplate template:
        :param str path_full:
        :param str path_rel:

        """
        self.template = template
        self.path_full = path_full
        self.path_rel= path_rel

    def __str__(self):
        return self.path_full

    @property
    def parent_paths(self):
        """A list of parent template paths."""
        paths = []

        path_rel = self.path_rel

        parent = self.template

        while True:
            parent = parent.parent

            if not parent:
                break

            path_full = os.path.join(parent.path, path_rel)

            if os.path.exists(path_full):
                # Check parent file exists in template.
                paths.append(os.path.join(parent.name, path_rel))

            if parent.is_default:
                break

        return paths
