from __future__ import absolute_import

from makeapp.appconfig import Config


class DjangoConfig(Config):

    parent_template = ['pytest']


makeapp_config = DjangoConfig
