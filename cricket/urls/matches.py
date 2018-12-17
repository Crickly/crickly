# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python Imports
# -- None


# Django Imports
from django.conf.urls import url


# Project Imports
from cricket.views.match import (Index, Fixtures, Results, Match)


# Define URL patterns
urlpatterns = [
    # url(regex, view, name)
    url(r'^$', Index.as_view(), name='index'),
    url(r'^fixtures/$', Fixtures.as_view(), name='fixtures'),
    url(r'^results/$', Results.as_view(), name='results'),
    url(r'^(?P<match_id>[0-9]*)/$', Match.as_view(), name='match'),
]
