from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class {{ package_name_capital }}Config(AppConfig):
    """Application configuration."""

    name = '{{ package_name }}'
    verbose_name = _('{{ package_name_capital }}')

    # def ready(self):
    #     """Application initialization."""

