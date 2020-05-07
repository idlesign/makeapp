from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {{ module_name_capital }}Config(AppConfig):
    """Application configuration."""

    name = '{{ module_name }}'
    verbose_name = _('{{ module_name_capital }}')

    # def ready(self):
    #     """Application initialization."""

