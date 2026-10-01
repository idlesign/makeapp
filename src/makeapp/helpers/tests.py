import re
from functools import partial
from itertools import product
from pathlib import Path
from pprint import pformat
from sys import version_info

import yaml

from ..exceptions import CommandError, ProjectorExeption
from ..utils import LOG, Uv


class TestsHelper:

    _RE_VAR = re.compile(r'\$\{\{\s*([\w-]+)\s*\}\}')
    _RE_VALID_IDENT = re.compile(r'[^a-zA-Z0-9]')
    _RE_PYTHON_VERSION = re.compile(
        r'^\s*version(?:_info)?\s*=\s*(\d+)\.(\d+)'
    )

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
        candidates = [
            (name, job.get('strategy', {}).get('matrix', {}))
            for name, job in jobs.items()
            if 'python-version' in job.get('strategy', {}).get('matrix', {})
        ]
        if not candidates:
            raise ProjectorExeption('No test matrix with `python-version` found.')

        by_name = dict(candidates)
        job_name = next(
            (name for name in ('tests', 'test', 'build') if name in by_name),
            candidates[0][0],
        )
        matrix = dict(by_name[job_name])
        exclusions = matrix.pop('exclude', [])
        keys = matrix.keys()
        values = matrix.values()
        combinations = []

        def norm(val) -> float | str:
            try:
                return float(val)
            except (ValueError, TypeError):
                return f'{val}'

        for combined in product(*values):
            combination = dict(zip(keys, combined, strict=False))
            is_excluded = False
            for exclusion in exclusions:
                if all(f'{norm(combination.get(key))}' == f'{norm(val)}' for key, val in exclusion.items()):
                    is_excluded = True
                    break

            if not is_excluded:
                combinations.append(combination)

        return combinations

    @classmethod
    def is_venv_compatible(cls, venv_dir: Path, python_version: str) -> bool:
        """Return whether a virtual environment uses the requested Python version."""
        expected = re.match(r'^(\d+)\.(\d+)', python_version)
        config_path = venv_dir / 'pyvenv.cfg'
        if expected is None or not config_path.is_file():
            return False

        for line in config_path.read_text().splitlines():
            if actual := cls._RE_PYTHON_VERSION.match(line):
                return actual.groups() == expected.groups()

        return False

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

        environments = []
        for combination in matrix:
            python_version = combination.get('python-version')
            if not python_version:
                python_version = f'{version_info.major}.{version_info.minor}'
            python_version = f'{python_version}'
            ident_chunks = [make_valid_ident(f'py{python_version}')]
            deps_resolved = []
            for dep in deps:
                dep = apply_ctx(dep, combination)
                deps_resolved.append(dep)
                ident_chunks.append(make_valid_ident(dep))

            ident = "_".join(ident_chunks)
            if not only or ident in only:
                environments.append((ident, combination, python_version, deps_resolved))

        reuse_project_venv = (
            len(environments) == 1
            and self.is_venv_compatible(Path('.venv'), environments[0][2])
        )

        stats = {
            self.KEY_OK: [],
            self.KEY_FAIL: [],
        }

        for ident, combination, python_version, deps_resolved in environments:
            LOG.info(f'Running: {ident}: {combination} ...')

            venv_dir = '.venv' if reuse_project_venv else f'.venv_ma/{ident}'
            if reuse_project_venv:
                LOG.info(f'Reusing project virtual environment: {venv_dir}')
            execute = partial(Uv.exec, env={
                'VIRTUAL_ENV': venv_dir,
                'UV_PROJECT_ENVIRONMENT': venv_dir,
            })
            status = self.KEY_OK

            try:
                if reuse_project_venv:
                    command = ['run', '--group', 'tests', '--python', python_version]
                    for dep in deps_resolved:
                        command.extend(['--with', dep])
                    execute([*command, 'pytest'])

                else:
                    execute(['sync', '--only-group', 'tests', '--python', python_version])

                    if deps_resolved:
                        execute(['pip', 'install', *deps_resolved, '--python', venv_dir])

                    execute(['run', 'pytest'])

            except CommandError:
                status = self.KEY_FAIL
                continue

            finally:
                stats[status].append(ident)

        return stats
