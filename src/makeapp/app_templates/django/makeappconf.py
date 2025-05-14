from makeapp.appconfig import Config


class DjangoConfig(Config):

    cleanup: list[str] = ['tests']


makeapp_config = DjangoConfig
