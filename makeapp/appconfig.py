from collections import OrderedDict
from time import sleep

import click

from .utils import _compat  # exposed as API

if False:  # pragma: nocover
    from .apptemplate import AppTemplate


class ConfigMeta(type):

    def __new__(cls, name, bases, dict_):
        new_type = type.__new__(cls, name, bases, dict_)

        for key, val in dict_.items():
            if isinstance(val, ConfigSetting):
                val.name = key

        return new_type


class ConfigSetting(object):

    name = None  # Runtime bound by metaclass.

    def __init__(self, title, default=None, type=None):
        self.title = title
        self.default = default
        self.type = type

    def __get__(self, instance, owner):
        """Allows convenient IDE-friendly access from Config
        heirs to settings defined in them.

        :param Config instance:
        :param type(Config) owner:

        """
        app_template = instance.app_template
        return app_template.maker.settings['%s_%s' % (app_template.name, self.name)]


class Config(_compat.with_metaclass(ConfigMeta)):
    """Base for application template configuration."""

    parent_template = None

    def __init__(self, app_template):
        """

        :param AppTemplate app_template:
        """
        self.app_template = app_template
        self.logger = app_template.maker.logger

        settings = OrderedDict()

        for key, val in self.__class__.__dict__.items():
            if isinstance(val, ConfigSetting):
                settings['%s_%s' % (app_template.name, key)] = val

        self.settings = settings

    def hook_configure(self):
        """Executed on rollout configuration."""

        settings_conf = self.settings

        if not settings_conf:
            return

        app_template = self.app_template
        settings_current = app_template.maker.settings
        settings_gathered = OrderedDict()
        advertise_template = True

        for setting_name, settings_obj in settings_conf.items():

            current_value = settings_current.get(setting_name)

            if current_value is None:

                if advertise_template:
                    click.secho(
                        "Gathering settings for '%s' application template ..." %
                        app_template.name,
                        fg='blue'
                    )
                    advertise_template = False

                current_value = click.prompt(
                    '%s (%s)' % (settings_obj.title, setting_name),
                    default=settings_obj.default,
                    type=settings_obj.type,
                )

                settings_gathered[setting_name] = current_value

        app_template.maker.update_settings(settings_gathered)

    def print_banner(self, text):
        """Prints out a banner with the given text.

        :param str text:

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
