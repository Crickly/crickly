# -*- coding: utf-8 -*-
from django.conf.urls import url
from crickly.core.views import stats

# Define URL patterns
urlpatterns = [
    # url(regex, view, name)
    url(r'^$', stats.index, name='index'),
    url(r'^bowling/$', stats.bowling, name='bowling'),
    url(r'^batting/$', stats.batting, name='batting'),
    url(r'^fielding/$', stats.fielding, name='fielding'),
]
