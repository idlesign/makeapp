from shutil import rmtree

from ..utils import LOG, check_command, get_user_dir, read_ini, run_command


class DistHelper:
    """Encapsulates Python distribution related logic."""

    check_command('uv', hint='uv')

    @classmethod
    def run_command_uv(cls, command: str, *, env: dict = None) -> list[str]:
        """Basic command runner."""
        return run_command(f'uv {command}', env=env)

    @classmethod
    def upload(cls):
        """Builds a package and uploads it to PyPI."""

        rmtree('dist/', ignore_errors=True)  # cleanup

        pypirc_file = get_user_dir() / '.pypirc'
        env_vars = None

        if pypirc_file.exists():
            cfg = read_ini(pypirc_file)
            if cfg.has_section('pypi') and (token := cfg.get('pypi', 'password')):
                env_vars = {
                    'UV_PUBLISH_TOKEN': token
                }

        if not env_vars:
            LOG.warning(f'PyPI credentials not found in {pypirc_file}')

        cls.run_command_uv('build')
        cls.run_command_uv('publish', env=env_vars)
