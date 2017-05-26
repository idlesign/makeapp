from django import VERSION
from django.conf.urls import url


urlpatterns = [
]

if VERSION < (1, 10):
    from django.conf.urls import patterns
    urlpatterns.insert(0, '')
    urlpatterns = patterns(*urlpatterns)
