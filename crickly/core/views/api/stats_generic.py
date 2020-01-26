# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
# --None

# Python imports
from datetime import date

# Project imports
from crickly.core.models import Player, Team
from crickly.core.views.api import BaseView
from crickly.core.views.exceptions import AbstractClassError, kwargError


class View(BaseView):
    '''
        A view which ... TODO
    '''
    def __init__(self, **kwargs):
        if self.abstract:
            raise AbstractClassError
        super(View, self).__init__(**kwargs)

    abstract = True
    order_by_options = []
    order_by_functions = {}

    def check_order_by_setup(self):
        if sorted(self.order_by_options) != sorted(self.order_by_functions.keys()):
            raise ValueError(
                'order_by_options and order_by_functions are not consistent. ({0} != {1})'.format(
                    self.order_by_options, self.order_by_functions.keys()
                )
            )

    def validate_year(self, year):
        if year != 'all':
            try:
                if int(year) not in range(2010, date.today().year + 1):
                    raise kwargError(
                        'Year not in range (2010 - {})'.format(date.today().year)
                    )
            except ValueError:
                raise kwargError(
                    'Year not in range (2010 - {} / all)'.format(date.today().year)
                )

    def validate_team(self, team):
        if team != 'all':
            current_teams = Team.objects.filter(club__home_club=True).values_list('id', flat=True)
            if team not in current_teams:
                raise kwargError(
                    'Team not a valid option ({})'.format(
                        '/'.join(map(str, current_teams))
                    )
                )

    def validate_order_by(self, order_by):
        if order_by not in self.order_by_options:
            raise kwargError(
                '''Order_by is not a valid option
                (name/overs/maidens/runs/average/wickets/economy/fantasy)''')

    def validate_display_count(self, display_count):
        if display_count not in ['20', '50', 'all']:
            raise kwargError('Display_count is not a valid option (20/50/all)')

    def get_years(self):
        year = self.get_kwarg('year')
        if year == 'all':
            year = range(2010, date.today().year + 1)
        else:
            year = [year]
        return year

    def get_teams(self):
        team = self.get_kwarg('team')
        if team == 'all':
            team = Team.objects.filter(club__home_club=True).values_list('id', flat=True)
        else:
            team = [team]
        return team

    def get_display_count(self):
        return self.get_kwarg('display_count')

    def get_order_by_function(self):
        order_by = self.get_kwarg('order_by')
        return self.order_by_functions[order_by]

    def get_players(self):
        return Player.objects.filter(club__home_club=True)

    def get_sorted_players(self, years, teams):
        f = self.get_order_by_function()
        return f(self.get_filtered_players(years, teams), years, teams)

    def get_filtered_players(self, years, teams):
        return filter(
            lambda a: self.filter_function(a, years, teams),
            self.get_players()
        )

    def get_shortened_players(self, years, teams):
        players = self.get_sorted_players(years, teams)
        if self.get_display_count() == 'all':
            return players
        else:
            return players[:int(self.get_display_count())]

    def get_important_info(self, year, team):
        players = self.get_shortened_players(year, team)
        return [self.important_info(player, year, team) for player in players]

    def get(self, request, **kwargs):
        try:
            # Check order by set up correctly
            self.check_order_by_setup()

            # Validate KwArgs
            self.validate_kwargs()

            # Get year and team
            year = self.get_years()
            team = self.get_teams()

            return self.JsonResponse(
                {
                    'stats': self.get_important_info(year, team),
                    'kwargs': self.kwargs,
                }
            )
        except kwargError as e:
            return self.error_message(str(e))
        except kwargError:
            return self.error_message()
