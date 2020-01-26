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
        'name', 'overs', 'maidens', 'runs', 'average',
        'wickets', 'economy',
    ]

    order_by_functions = {
        'name': lambda a, b, c: a.order_by('player_name'),
        'overs': lambda a, b, c: sorted(a, key=lambda d: d.get_overs(b, c), reverse=True),
        'maidens': lambda a, b, c: sorted(a, key=lambda d: d.get_maidens(b, c), reverse=True),
        'runs': lambda a, b, c: sorted(a, key=lambda d: d.get_bowl_runs(b, c), reverse=True),
        'average': lambda a, b, c: sorted(
            a,
            key=lambda d: d.get_bowl_average(
                b,
                c
            ) if d.get_bowl_average(b, c) != '-' else 1000000
        ),
        'wickets': lambda a, b, c: sorted(a, key=lambda d: d.get_wickets(b, c), reverse=True),
        'economy': lambda a, b, c: sorted(a, key=lambda d: d.get_economy(b, c)),
    }

    def filter_function(self, player, years, teams):
        return player.has_bowled(years, teams)

    def important_info(self, player, years, teams):
        return{
            'player_name': player.player_name,
            'overs': floatformat(player.get_overs(years, teams)),
            'maidens': player.get_maidens(years, teams),
            'runs': player.get_bowl_runs(years, teams),
            'wickets': player.get_wickets(years, teams),
            'average': floatformat(player.get_bowl_average(years, teams)),
            'economy': floatformat(player.get_economy(years, teams)),
            'wickets_5': player.get_5_wickets(years, teams),
        }
