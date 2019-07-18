from collections import OrderedDict

import click

from .utils import run_command, check_command, temp_dir, replace_infile, _compat  # exposed as API

if False:  # pragma: nocover
    from .apptemplate import AppTemplate


class ConfigSetting(object):

    def __init__(self, title, default=None, type=None):
        self.title = title
        self.default = default
        self.type = type


class Config(object):
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
        app_template = self.app_template
        settings_current = app_template.maker.settings

        if not settings_conf:
            return

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

    def hook_rollout_pre(self):
        """Executed before application skeleton rollout."""

    def hook_rollout_post(self):
        """Executed after application skeleton rollout."""
