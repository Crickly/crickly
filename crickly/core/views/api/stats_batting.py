# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.template.defaultfilters import floatformat

# Python imports
# --None

# Project imports
from crickly.core.views.api import BaseStatsView


class View(BaseStatsView):
    '''
        A view with creates a JSONResponse containing fixtures in the given period:
        wk - week
        mth - month
        sn - season ( defined to finish on 31st December )
    '''
    abstract = False
    order_by_options = [
        'name', 'games', 'innings', 'runs', 'par_runs',
        'average', 'no', 'highscore',
    ]

    order_by_functions = {
        'name': lambda a, b, c: a.order_by('player_name'),
        'games': lambda a, b, c: sorted(a, key=lambda d: d.get_games(b, c), reverse=True),
        'innings': lambda a, b, c: sorted(a, key=lambda d: d.get_innings(b, c), reverse=True),
        'runs': lambda a, b, c: sorted(a, key=lambda d: d.get_runs(b, c), reverse=True),
        'par_runs': lambda a, b, c: sorted(a, key=lambda d: d.get_par_runs(b, c), reverse=True),
        'average': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_average(
                b,
                c
            ) if d.get_average(b, c) != '-' else -1,
            reverse=True,
        ),
        'no': lambda a, b, c: sorted(a, key=lambda d: d.get_not_outs(b, c), reverse=True),
        'highscore': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_high_score(b, c),
            reverse=True
        ),
    }

    def filter_function(self, player, years, teams):
        return player.has_batted(years, teams)

    def important_info(self, player, year, team):
        return {
            'player_name': player.player_name,
            'games': player.get_games(year, team),
            'innings': player.get_innings(year, team),
            'not_outs': player.get_not_outs(year, team),
            'runs': player.get_runs(year, team),
            'par_runs': player.get_par_runs(year, team),
            'high_score': player.get_high_score(year, team),
            'average': floatformat(player.get_average(year, team)),
            'runs_50s': player.get_50s(year, team),
            'runs_100s': player.get_100s(year, team),
        }
