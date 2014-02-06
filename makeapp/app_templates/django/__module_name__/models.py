from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import python_2_unicode_compatible


# @python_2_unicode_compatible
# class MyModel(models.Model):
#
#     title = models.CharField(_('Title'), max_length=100, help_text=_('Description'))
#
#     class Meta:
#         verbose_name = _('Model')
#         verbose_name_plural = _('Models')
#
#     def __str__(self):
#         return self.title
