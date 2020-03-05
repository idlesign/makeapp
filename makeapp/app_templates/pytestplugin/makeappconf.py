from makeapp.appconfig import Config


class PytestPluginConfig(Config):

    parent_template = ['pytest']


makeapp_config = PytestPluginConfig
