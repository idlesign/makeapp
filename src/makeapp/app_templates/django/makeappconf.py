from makeapp.appconfig import Config


class DjangoConfig(Config):

    parent_template: list[str] = ['pytest']
    cleanup: list[str] = ['tests']


makeapp_config = DjangoConfig
