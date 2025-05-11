from typing import List

from makeapp.appconfig import Config


class DjangoConfig(Config):

    parent_template: List[str] = ['pytest']
    cleanup: List[str] = ['tests']


makeapp_config = DjangoConfig
