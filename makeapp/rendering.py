import os

from jinja2 import Environment, FileSystemLoader

from .apptemplate import TemplateFile
from .utils import chdir


class ContextMutator(object):
    """Mutator applying additional transformations to template get_context."""

    def __init__(self, maker):
        """
        :param AppMaker maker:
        """
        self._maker = maker
        self._context = maker.settings

    def get_app_title_rst(self, continuation=''):
        """Returns application title for RST."""

        if continuation:
            continuation = ' ' + continuation

        title = self._context['app_name'] + continuation
        title = '%s\n%s' % (title, '=' * len(title))

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


class Renderer(object):
    """Performs file rendering."""

    def __init__(self, maker, paths):
        self.context_mutator = ContextMutator(maker=maker)

        paths = paths[:]
        paths.extend([
            # self.path_templates_license,
            '.',  # Use current working dir.
        ])

        self.env = Environment(
            loader=DynamicParentLoader(paths),
            keep_trailing_newline=True,
            trim_blocks=True,
        )

    def render(self, filename):
        """Renders file contents with settings as get_context.

        :param str|unicode|TemplateFile filename:
        :rtype: str|unicode
        """
        context = self.context_mutator.get_context()

        filename_ = '%s' % filename

        with chdir(os.path.dirname(filename_)):
            template = self.env.get_template(os.path.basename(filename_))

        if isinstance(filename, TemplateFile):
            # Let's compute template inheritance hierarchy for `parent_template`
            # context dynamic variable.
            parent_paths = filename.parent_paths

            if parent_paths:
                context['parent_template'] = DynamicParentTemplate(parent_paths)

        rendered = template.render(**context)

        return rendered


class DynamicParentTemplate(object):
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
            raise IndexError('No more parents to pop. Initial parents: %s' % self.parents_initial)

        return current

    def __repr__(self):
        return 'Namespace'  # hack


class DynamicParentLoader(FileSystemLoader):
    """Allows dynamic swapping of `parent_template` template context variable."""

    def get_source(self, environment, template):

        is_dynamic = isinstance(template, DynamicParentTemplate)

        if is_dynamic:
            template = '%s' % template.current

        source, filename, uptodate = super(DynamicParentLoader, self).get_source(environment, template)

        if is_dynamic:
            # Prevent `parent_template` context variable caching.
            uptodate = lambda: False

        return source, filename, uptodate
