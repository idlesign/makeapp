from pathlib import Path
from shutil import rmtree
from time import sleep
from typing import Any, Type, List

import click

if False:  # pragma: nocover
    from .apptemplate import AppTemplate  # noqa


class ConfigMeta(type):

    def __new__(cls, name: str, bases: tuple, dict_: dict):
        new_type = type.__new__(cls, name, bases, dict_)

        for key, val in dict_.items():
            if isinstance(val, ConfigSetting):
                val.name = key

        return new_type


class ConfigSetting:

    name = None  # Runtime bound by metaclass.

    def __init__(self, title: str, default: Any = None, type: Any = None):
        self.title = title
        self.default = default
        self.type = type

    def __get__(self, instance: 'Config', owner: Type['Config']) -> Any:
        """Allows convenient IDE-friendly access from Config
        heirs to settings defined in them.

        :param instance:
        :param owner:

        """
        app_template = instance.app_template

        return app_template.maker.settings[f'{app_template.name}_{self.name}']


class Config(metaclass=ConfigMeta):
    """Base for application template configuration."""

    parent_template: List[str] = None
    """Parent template names."""

    cleanup: List[str] = None
    """Paths to cleanup after rollout."""

    def __init__(self, app_template: 'AppTemplate'):
        """

        :param app_template:

        """
        self.app_template = app_template
        self.logger = app_template.maker.logger

        settings = {}

        for key, val in self.__class__.__dict__.items():

            if isinstance(val, ConfigSetting):
                settings[f'{app_template.name}_{key}'] = val

        self.settings = settings

    def hook_configure(self):
        """Executed on rollout configuration."""

        settings_conf = self.settings

        if not settings_conf:
            return

        app_template = self.app_template
        settings_current = app_template.maker.settings
        settings_gathered = {}
        advertise_template = True

        for setting_name, settings_obj in settings_conf.items():

            current_value = settings_current.get(setting_name)

            if current_value is None:

                if advertise_template:
                    click.secho(
                        f"Gathering settings for '{app_template.name}' application template ...",
                        fg='blue'
                    )
                    advertise_template = False

                current_value = click.prompt(
                    f'{settings_obj.title} ({setting_name})',
                    default=settings_obj.default,
                    type=settings_obj.type,
                )

                settings_gathered[setting_name] = current_value

        app_template.maker.update_settings(settings_gathered)

    def print_banner(self, text: str):
        """Prints out a banner with the given text.

        :param text:

        """
        max_line_len = max(map(len, text.splitlines()))
        text = text + '\n' + '=' * max_line_len + '\n'

        self.logger.warning(text)
        sleep(1)

    def hook_rollout_init(self):
        """Executed on skeleton rollout initialization."""

    def hook_rollout_pre(self):
        """Executed before application skeleton rollout."""

    def hook_rollout_post(self):
        """Executed after application skeleton rollout."""
        cleanup = self.cleanup or []

        for path in cleanup:
            path = Path(path).absolute()
            self.logger.info(f'Cleanup {path} ...')
            rmtree(path, ignore_errors=True)
