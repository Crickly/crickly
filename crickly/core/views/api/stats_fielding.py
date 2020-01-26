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
        'name', 'games',
        'wk_catches', 'wk_stumpings', 'wk_total',
        'fld_catches', 'fld_run_outs', 'fld_total',
    ]

    order_by_functions = {
        'name': lambda a, b, c: a.order_by('player_name'),
        'games': lambda a, b, c: sorted(a, key=lambda d: d.get_games(b, c), reverse=True),
        'wk_catches': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_keeping_catches(b, c),
            reverse=True
        ),
        'wk_stumpings': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_stumpings(b, c),
            reverse=True
        ),
        'wk_total': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_keeping_wickets(
                b,
                c
            ),
            reverse=True,
        ),
        'fld_catches': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_fielding_catches(b, c),
            reverse=True
        ),
        'fld_run_outs': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_run_outs(b, c),
            reverse=True,
        ),
        'fld_total': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_fielding_wickets(b, c),
            reverse=True,
        ),
    }

    def filter_function(self, player, years, teams):
        return player.played_game(years, teams)

    def important_info(self, player, year, team):
        return {
            'player_name': player.player_name,
            'games': player.get_games(year, team),
            'wk_catches': player.get_keeping_catches(year, team),
            'wk_stumpings': player.get_stumpings(year, team),
            'wk_total': player.get_keeping_wickets(year, team),
            'fld_catches': player.get_fielding_catches(year, team),
            'fld_run_outs': player.get_run_outs(year, team),
            'fld_total': player.get_fielding_wickets(year, team),
        }
