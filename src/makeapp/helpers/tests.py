import re
from functools import partial
from itertools import product
from pathlib import Path
from pprint import pformat
from sys import version_info

import yaml

from ..exceptions import CommandError
from ..utils import LOG, Uv


class TestsHelper:

    _RE_VAR = re.compile(r'\$\{\{\s*([\w-]+)\s*\}\}')
    _RE_VALID_IDENT = re.compile(r'[^a-zA-Z0-9]')

    KEY_OK = 'OK'
    KEY_FAIL = 'FAIL'

    def __init__(self, *, settings: dict, only: list[str] | None = None):
        self._settings = settings
        self._only = set(only or [])

    @classmethod
    def apply_context(cls, text: str, context: dict) -> str:
        """Apply context to a text (resolves variables).

        :param text:
        :param context:
        """
        def replace(match):
            var_name = match.group(1)
            return f'{context.get(var_name, match.group(0))}'

        return cls._RE_VAR.sub(replace, text)

    @classmethod
    def get_matrix_github(cls, fpath: Path):
        with fpath.open() as f:
            config = yaml.safe_load(f)

        jobs = config.get('jobs', {})
        job_name = list(jobs.keys())[0]
        matrix = jobs[job_name].get('strategy', {}).get('matrix', {})
        exclusions = matrix.pop('exclude', [])
        keys = matrix.keys()
        values = matrix.values()
        combinations = []

        for combined in product(*values):
            combination = dict(zip(keys, combined, strict=False))
            is_excluded = False
            for exclusion in exclusions:
                if all(f'{combination.get(key)}' == f'{val}' for key, val in exclusion.items()):
                    is_excluded = True
                    break

            if not is_excluded:
                combinations.append(combination)

        return combinations

    def run_tests(self) -> dict[str, list[str]]:
        settings = self._settings

        workflow_github = Path(settings.get('workflow_github') or 'python-package.yml')
        if len(workflow_github.parts) == 1:
            workflow_github = Path('.github', 'workflows', workflow_github)

        matrix = self.get_matrix_github(workflow_github)
        apply_ctx = self.apply_context
        make_valid_ident = partial(self._RE_VALID_IDENT.sub, '')
        deps = settings.get('deps') or []
        only = self._only

        matrix_lines = '\n  '.join(' '.join(f"{key}:{value}" for key, value in line.items()) for line in matrix)
        LOG.info(f'Test matrix:\n  {matrix_lines}')

        stats = {
            self.KEY_OK: [],
            self.KEY_FAIL: [],
        }

        for combination in matrix:

            python_version = combination.get('python-version') or f"{version_info.major}.{version_info.minor}"
            ident_chunks = [make_valid_ident(f'py{python_version}')]
            deps_resolved = []
            for dep in deps:
                dep = apply_ctx(dep, combination)
                deps_resolved.append(f'"{dep}"')
                ident_chunks.append(make_valid_ident(dep))

            ident = "_".join(ident_chunks)

            if not only or ident in only:
                LOG.info(f'Running: {ident}: {combination} ...')

                venv_dir = f'.venv_ma/{ident}'
                execute = partial(Uv.exec, env={
                    'VIRTUAL_ENV': venv_dir,
                    'UV_PROJECT_ENVIRONMENT': venv_dir,
                })
                status = self.KEY_OK

                try:
                    execute(f'sync --only-group tests --python {python_version}')

                    if deps_resolved := ' '.join(deps_resolved):
                        execute(f'pip install {deps_resolved} --python {venv_dir}')

                    execute('run pytest')

                except CommandError:
                    status = self.KEY_FAIL
                    continue

                finally:
                    stats[status].append(ident)

        return stats
