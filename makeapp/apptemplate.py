import importlib.util
import os
from typing import Type, Dict, Tuple

from .appconfig import Config
from .exceptions import AppMakerException

if False:  # pragma: nocover
    from .appmaker import AppMaker


class AppTemplate:
    """Represents an application template."""

    config_filename = 'makeappconf.py'
    config_attr = 'makeapp_config'

    def __init__(self, maker: 'AppMaker', name: str, path: str, parent: 'AppTemplate' = None):
        """

        :param maker:
        :param name:
        :param path:
        :param parent:

        """
        self.maker = maker
        self.name = name
        self.path = path
        self.parent = parent
        self.config = self._read_config()
        self._process_config()

    def __str__(self):
        return f'{self.name}: {self.path}'

    @property
    def is_default(self):
        """Whether current template is default (root)."""
        return self.name == self.maker.template_default_name

    def _read_config(self) -> Config:
        """Reads template's config.

        If not found, dummy config object is returned.

        """
        module_fake_name = f'makeapp.config.{self.name}'

        config_path = os.path.join(self.path, self.config_filename)

        if os.path.exists(config_path):

            spec = importlib.util.spec_from_file_location(module_fake_name, config_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            config: Type[Config] = getattr(module, self.config_attr, None)

            if not issubclass(config, Config):
                raise AppMakerException(
                    f"Unable to load config class for '{self.name}' template. "
                    f"Make sure '{config_path}' file has '{self.config_attr}' "
                    'attribute having value of AppConfig heir.')

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

    def run_config_hook(self, hook_name: str) -> bool:
        """Runs a hook function from app config template if defined there.
        Returns `True` if a hook has been run.

        :param hook_name:

        """
        hook_name = f'hook_{hook_name}'
        hook_func = getattr(self.config, hook_name, None)

        if hook_func:
            hook_func()
            return True

        return False

    def get_files(self) -> Dict[str, 'TemplateFile']:
        """Returns a mapping of relative filenames to TemplateFiles objects."""

        template_files = {}

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
    def contribute_to_maker(cls, maker: 'AppMaker', template: str, parent: 'AppTemplate') -> 'AppTemplate':
        """
        :param maker:
        :param template:
        :param parent:

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
    def _find(cls, name_or_path: str, search_paths: Tuple[str, ...]) -> Tuple[str, str]:
        """Searches a template by it's name or in path.
        Returns a tuple (template_name, template_path)

        :param name_or_path:
        :param search_paths:

        """
        for supposed_path in search_paths:
            if '/' in supposed_path and os.path.exists(supposed_path):
                path = str(os.path.abspath(supposed_path))
                return path.split('/')[-1], path

        raise AppMakerException(
            f"Unable to find application template {name_or_path}. "
            "Searched \n%s" % '\n  '.join(search_paths))


class TemplateFile:
    """Represents app template file info."""

    __slots__ = ['template', 'path_full', 'path_rel']

    def __init__(self, template: AppTemplate, path_full: str, path_rel: str):
        """
        :param template:
        :param path_full:
        :param path_rel:

        """
        self.template = template
        self.path_full = path_full
        self.path_rel = path_rel

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
