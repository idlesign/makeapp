import os
from typing import Union

from jinja2 import Environment, FileSystemLoader

from .apptemplate import TemplateFile
from .utils import chdir

if False:  # pragma: nocover
    from .appmaker import AppMaker


class ContextMutator:
    """Mutator applying additional transformations to template get_context."""

    def __init__(self, maker: 'AppMaker'):
        """
        :param maker:

        """
        self._maker = maker
        self._context = maker.settings

    def get_app_title_rst(self, continuation=''):
        """Returns application title for RST."""

        if continuation:
            continuation = ' ' + continuation

        title = self._context['app_name'] + continuation
        title = f"{title}\n{'=' * len(title)}"

        return title

    def get_context(self):
        maker = self._maker
        context = dict(self._context)

        license_tuple = maker.LICENSES.get(context['license'], maker.LICENSES[maker.default_license])

        context.update({
            'get_app_title_rst': self.get_app_title_rst,
            'license_title': license_tuple[0],
            'license_title_pypi': license_tuple[1],
            'python_version_major': context['python_version'].split('.')[0],
            'module_name_capital': context['module_name'].capitalize(),
        })

        return context


class Renderer:
    """Performs file rendering."""

    def __init__(self, maker, paths):
        self.context_mutator = ContextMutator(maker=maker)

        paths = list({}.fromkeys(paths).keys())  # Unique.
        paths.insert(0, '.')  # Use current working dir.

        self.env = Environment(
            loader=DynamicParentLoader(paths),
            keep_trailing_newline=True,
            trim_blocks=True,
        )

    def render(self, filename: Union[str, TemplateFile]) -> str:
        """Renders file contents with settings as get_context.

        :param filename:

        """
        context = self.context_mutator.get_context()

        if isinstance(filename, TemplateFile):
            # Let's compute template inheritance hierarchy for `parent_template`
            # context dynamic variable.
            parent_paths = filename.parent_paths

            if parent_paths:
                parent_template = DynamicParentTemplate(parent_paths)

            else:
                parent_template = f'no-parent-for/{filename.path_rel}'

            context['parent_template'] = parent_template

            # Use exact location.
            template = self.env.get_template(f'{filename.template.name}/{filename.path_rel}')

        else:
            filename_ = f'{filename}'

            # Try to pick file by basename.
            with chdir(os.path.dirname(filename_)):
                template = self.env.get_template(os.path.basename(filename_))

        rendered = template.render(**context)

        return rendered


class DynamicParentTemplate:
    """Represents jinja dynamic `parent_template` variable."""

    def __init__(self, parents):
        parents = parents[::-1]
        self.parents = parents
        self.parents_initial = parents[:]

    @property
    def current(self):

        try:
            current = self.parents.pop()

        except IndexError:
            # Mostly for template inheritance debug purposes.
            raise IndexError(f'No more parents to pop. Initial parents: {self.parents_initial}.')

        return current

    def __repr__(self):
        return 'Namespace'  # hack


class DynamicParentLoader(FileSystemLoader):
    """Allows dynamic swapping of `parent_template` template context variable."""

    def get_source(self, environment, template):

        is_dynamic = isinstance(template, DynamicParentTemplate)

        if is_dynamic:
            template = f'{template.current}'

        source, filename, uptodate = super().get_source(environment, template)

        if is_dynamic:
            # Prevent `parent_template` context variable caching.
            uptodate = lambda: False

        return source, filename, uptodate
