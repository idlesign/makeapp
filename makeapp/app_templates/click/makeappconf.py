from __future__ import absolute_import

from makeapp.appconfig import Config


class ClickConfig(Config):

    parent_template = ['console']


makeapp_config = ClickConfig
