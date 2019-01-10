# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cricket.core.views.api.generic import View as BaseView
from cricket.core.views.api.stats_generic import View as BaseStatsView
from cricket.core.views.api.fixtures import View as FixtureView
from cricket.core.views.api.results import View as ResultView
from cricket.core.views.api.stats_bowling import View as StatsBowlingView
from cricket.core.views.api.stats_batting import View as StatsBattingView
from cricket.core.views.api.stats_fielding import View as StatsFieldingView


__all__ = [
    'BaseView', 'BaseStatsView',
    'FixtureView', 'ResultView',
    'StatsBowlingView', 'StatsBattingView', 'StatsFieldingView',
]
