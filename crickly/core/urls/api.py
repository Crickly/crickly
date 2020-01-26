# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url

from crickly.core.views.api import (
    FixtureView, ResultView,
    StatsBowlingView, StatsBattingView, StatsFieldingView,
)

# Define URL Patterns
urlpatterns = [
    # url(regex, view, name)
    url(
        r'^results/(?P<year>[0-9]{4})/(?P<month>[0-9]{2})/$',
        ResultView.as_view(),
        name='results'
    ),
    url(
        r'^fixtures/(?P<period>[\w]+)/$',
        FixtureView.as_view(),
        name='fixtures'
    ),
    url(
        r'^stats/batting/(?P<year>[\w]+)/(?P<team>[\w]+)/(?P<order_by>[\w]+)/(?P<display_count>[\w]+)/$',
        StatsBattingView.as_view(),
        name="stats_batting",
    ),
    url(
        r'^stats/bowling/(?P<year>[\w]+)/(?P<team>[\w]+)/(?P<order_by>[\w]+)/(?P<display_count>[\w]+)/$',
        StatsBowlingView.as_view(),
        name="stats_bowling",
    ),
    url(
        r'^stats/fielding/(?P<year>[\w]+)/(?P<team>[\w]+)/(?P<order_by>[\w]+)/(?P<display_count>[\w]+)/$',
        StatsFieldingView.as_view(),
        name="stats_fielding",
    ),
]
