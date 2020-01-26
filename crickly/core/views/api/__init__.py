from crickly.core.views.api.generic import View as BaseView
from crickly.core.views.api.stats_generic import View as BaseStatsView
from crickly.core.views.api.fixtures import View as FixtureView
from crickly.core.views.api.results import View as ResultView
from crickly.core.views.api.stats_bowling import View as StatsBowlingView
from crickly.core.views.api.stats_batting import View as StatsBattingView
from crickly.core.views.api.stats_fielding import View as StatsFieldingView


__all__ = [
    'BaseView', 'BaseStatsView',
    'FixtureView', 'ResultView',
    'StatsBowlingView', 'StatsBattingView', 'StatsFieldingView',
]
