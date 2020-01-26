# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.shortcuts import render
from django.db.models import Min

# Python imports
from datetime import date

# Project imports
from crickly.core.models import Player, Team, MatchDate


def get_seasons():
    start_year = MatchDate.objects.all().aggregate(Min('year'))['year__min']
    return range(date.today().year, start_year - 1, -1)


def get_teams():
    return Team.objects.filter(club__home_club=True).order_by('name')


# Stats index view
def index(request):
    # Get club players
    players = Player.objects.filter(club__home_club=True).all()

    # Sort players and remove any that have none value
    top_wicket_takers = sorted(players, key=lambda a: a.get_wickets())[:-6:-1]
    top_wicket_takers = filter(lambda a: a.get_wickets() is not None, top_wicket_takers)
    top_run_scorers = sorted(players, key=lambda a: a.get_runs())[:-6:-1]
    top_run_scorers = filter(lambda a: a.get_runs() is not None, top_run_scorers)
    top_catch_takers = sorted(players, key=lambda a: a.get_catches())[:-6:-1]
    top_catch_takers = filter(lambda a: a.get_catches() is not None, top_catch_takers)
    return render(
        request,
        'crickly/stats/index.html',
        context={
            'current_season': date.today().year,
            'top_wicket_takers': top_wicket_takers,
            'top_run_scorers': top_run_scorers,
            'top_catch_takers': top_catch_takers,
        }
    )


# Stats batting view
def batting(request):
    # Get club players
    players = Player.objects.filter(club__home_club=True)
    # Sort players by runs
    players = reversed(sorted(players, key=lambda a: a.get_runs()))

    # Remove players who havent batted
    final_players = []
    for i in players:
        if i.has_batted():
            final_players.append(i)
    return render(
        request,
        'crickly/stats/batting.html',
        context={
            'players': final_players[:20],
            'seasons': get_seasons(),
            'teams': get_teams(),
        }
    )


# Stats bolwing view
def bowling(request):
    # Get club players
    players = Player.objects.filter(club__home_club=True)
    # Sort players by wickets taken
    players = reversed(sorted(players, key=lambda a: a.get_wickets()))

    # Remove players who havent bowled
    final_players = []
    for i in players:
        if i.has_bowled():
            final_players.append(i)
    return render(
        request,
        'crickly/stats/bowling.html',
        context={
            'players': final_players[:20],
            'teams': get_teams(),
            'seasons': get_seasons(),
        }
    )


# Stats fielding view
def fielding(request):
    # Get club players
    players = Player.objects.filter(club__home_club=True)
    # Sort players by fielding wickets
    players = reversed(sorted(players, key=lambda a: a.get_fielding_wickets()))
    # Remove players who havent played a game
    final_players = []
    for i in players:
        if i.played_game:
            final_players.append(i)
    return render(
        request,
        'crickly/stats/fielding.html',
        context={
            'players': final_players[:20],
            'teams': get_teams(),
            'seasons': get_seasons(),
        }
    )
