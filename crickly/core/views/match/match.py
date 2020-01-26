# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
# -- None

# Django imports
from django.shortcuts import render, get_object_or_404


# Project imports
from crickly.core.views.generic import ArgumentView
from crickly.core.views.exceptions import kwargError, notEnoughInningsError
from crickly.core.models import Match, Inning, BatPerformance, BowlPerformance


class View(ArgumentView):

    def validate_match_id(self, match_id):
        match = get_object_or_404(Match, id=match_id)
        self.add_context('match', match)
        if not match.full_scorecard and match.processing_issue:
            raise kwargError('Match has not got a scorecard')
        if match.result in ['A', 'C', 'CON']:
            raise kwargError('Match was not played')

    def get_context_value(self, key):
        if key not in self.context.keys():
            raise KeyError('Key not in context')
        return self.context[key]

    def get_innings(self):
        match = self.get_context_value('match')
        innings = Inning.objects.filter(match__id=match.id)
        inning_1 = None
        inning_2 = None
        if innings.count() != 2:
            raise notEnoughInningsError(
                'Only {} Innings!'.format(
                    innings.count()
                )
            )
        for inning in innings:
            if inning.inning_no == 1:
                inning_1 = inning
            else:
                inning_2 = inning
        self.add_context(
            'inning_1',
            inning_1
        )
        self.add_context(
            'inning_2',
            inning_2
        )

    def get_performances(self):
        match = self.get_context_value('match')
        # player_performances = Performance.objects.filter(match__id=match.id)
        bat_performances = BatPerformance.objects.filter(match__id=match.id)
        bowl_performances = BowlPerformance.objects.filter(match__id=match.id)

        inning_1 = False
        inning_2 = False
        for inning in Inning.objects.filter(match_id=match.id):
            if inning.inning_no == 1:
                inning_1 = True
            else:
                inning_2 = True
        if inning_1:
            self.add_context(
                'inning_1_bat',
                bat_performances.filter(
                    bat=True,
                    bat_inning_no=1,
                ).order_by(
                    'bat_position'
                )
            )

            self.add_context(
                'inning_1_bowl',
                bowl_performances.filter(
                    bowl=True,
                    bowl_inning_no=1,
                ).order_by(
                    'bowl_position'
                )
            )
        if inning_2:
            self.add_context(
                'inning_2_bat',
                bat_performances.filter(
                    bat=True,
                    bat_inning_no=2,
                ).order_by(
                    'bat_position'
                )
            )

            self.add_context(
                'inning_2_bowl',
                bowl_performances.filter(
                    bowl=True,
                    bowl_inning_no=2,
                ).order_by(
                    'bowl_position'
                )
            )

        # if not match.is_live_score() and match.team.fantasy_league:
        #     self.add_context(
        #         'kvcc_players',
        #         match_performances.filter(
        #             player__kvcc_player=True,
        #         ).order_by(
        #             'player__player_name'
        #         )
        #     )

    def get(self, request, **kwargs):
        self.clear_context()
        try:
            self.validate_kwargs()
            self.get_innings()
            self.get_performances()
            return render(
                request,
                'crickly/matches/match.html',
                context=self.get_context()
            )
        except kwargError:
            return render(
                request,
                'crickly/matches/notplayed.html',
                context=self.get_context()
            )
        except notEnoughInningsError:
            return render(
                request,
                'crickly/matches/basic.html',
                context=self.get_context()
            )
