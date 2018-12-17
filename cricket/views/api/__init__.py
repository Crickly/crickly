# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cricket.views.api.generic import View as BaseView
from cricket.views.api.stats_generic import View as BaseStatsView
from cricket.views.api.fixtures import View as FixtureView
from cricket.views.api.results import View as ResultView
from cricket.views.api.stats_bowling import View as StatsBowlingView
from cricket.views.api.stats_batting import View as StatsBattingView
from cricket.views.api.stats_fielding import View as StatsFieldingView


__all__ = [
    'BaseView', 'BaseStatsView',
    'FixtureView', 'ResultView',
    'StatsBowlingView', 'StatsBattingView', 'StatsFieldingView',
]
