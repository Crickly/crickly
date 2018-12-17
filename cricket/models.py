# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.db.models import Sum, F, Max, Q
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.urlresolvers import reverse
import pytz

from datetime import date, timedelta, datetime


def get_current_year():
    ''' Gets current year '''
    return date.today().year


class Club(models.Model):
    pc_id = models.CharField(max_length=8)
    name = models.CharField(max_length=255)
    pc_slug = models.CharField(max_length=255)


class PCTeam(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    pc_id = models.CharField(max_length=8)
    name = models.CharField(max_length=255, default='unsure')


class Ground(models.Model):
    club = models.ForeignKey('Club', on_delete=models.CASCADE)
    pc_id = models.CharField(max_length=8)
    name = models.CharField(max_length=255)


class MatchDate(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    date = models.DateField()

    def get_date(self):
        return date(self.year, self.month, self.day)

    def get_datetime(self):
        return datetime(self.year, self.month, self.day, 12, 0, 0, 0, pytz.UTC)


class Competition(models.Model):
    pc_id = models.CharField(max_length=8)
    name = models.CharField(max_length=255)
    competition_type = models.CharField(max_length=32)


class Umpire(models.Model):
    pc_id = models.CharField(max_length=31)
    name = models.CharField(max_length=255)


class UmpireAssignment(models.Model):
    umpire = models.ForeignKey('Umpire', on_delete=models.CASCADE)
    match = models.ForeignKey('Match', on_delete=models.CASCADE)


# Match model.
# Used for storing data about matches
class Match(models.Model):
    fk_team = models.ForeignKey('PlayCricketTeam', on_delete=models.CASCADE)
    fk_competition = models.ForeignKey('Competition', on_delete=models.CASCADE)
    fk_date = models.ForeignKey('MatchDate', on_delete=models.CASCADE)
    fk_ground = models.ForeignKey('Ground', on_delete=models.CASCADE)
    fk_home_team = models.ForeignKey('PCTeam', on_delete=models.CASCADE, related_name='home_team')
    fk_away_team = models.ForeignKey('PCTeam', on_delete=models.CASCADE, related_name='away_team')

    # Status
    status = models.CharField(max_length=10)
    last_updated = models.DateField()

    # Competition
    competition_name = models.CharField(max_length=255)
    competition_id = models.CharField(max_length=8)
    competition_type = models.CharField(max_length=32)

    # Match Data
    match_type = models.CharField(max_length=64)
    game_type = models.CharField(max_length=32)
    match_id = models.CharField(max_length=8, unique=True)

    # Match Date
    match_date = models.DateField()
    season = models.CharField(
        max_length=4,
        default=get_current_year
    )

    # Ground
    ground_name = models.CharField(max_length=255)
    ground_id = models.CharField(max_length=8)

    # Home Team
    home_team_name = models.CharField(max_length=255)
    home_team_id = models.CharField(max_length=8)
    home_club_name = models.CharField(max_length=255)
    home_club_id = models.CharField(max_length=8)

    # Away Team
    away_team_name = models.CharField(max_length=255)
    away_team_id = models.CharField(max_length=8)
    away_club_name = models.CharField(max_length=255)
    away_club_id = models.CharField(max_length=8)

    # Umpire
    umpire_1_id = models.CharField(max_length=8, default='')
    umpire_1_name = models.CharField(max_length=255, default='')
    umpire_2_id = models.CharField(max_length=8, default='')
    umpire_2_name = models.CharField(max_length=255, default='')

    # Toss
    toss_won_by_team_id = models.CharField(max_length=8)
    toss = models.CharField(max_length=512)
    batted_first = models.CharField(max_length=8)

    # Result
    result = models.CharField(max_length=2)
    result_description = models.CharField(max_length=512)
    result_applied_to = models.CharField(max_length=8)
    match_notes = models.TextField()
    number_of_players = models.IntegerField(default=0)

    # Upload Status
    full_scorecard = models.BooleanField(default=False)
    processing_issue = models.BooleanField(default=False)

    # METHODS
    def new_match_description(self):
        if self.fk_home_team.club.pc_id == settings.PC_CLUB_ID:
            return self.fk_home_team.name + ' vs ' + self.fk_away_team.club.name + ' ' + self.fk_away_team.name
        else:
            return self.fk_away_team.name + ' vs ' + self.fk_home_team.club.name + ' ' + self.fk_home_team.name

    def match_description(self):
        ''' Creates a descriptive detail of the match '''
        if self.home_club_id == settings.PC_CLUB_ID:
            return self.home_team_name + ' vs ' + self.away_club_name + ' ' + self.away_team_name
        else:
            return self.away_team_name + ' vs ' + self.home_club_name + ' ' + self.home_team_name

    def is_live_score(self):
        return self.result == 'M'

    def __str__(self):
        # Gives useful info when using shell
        return self.match_id

    def get_absolute_url(self):
        return reverse('matches:match', kwargs={'match_id': self.id})

    def opposition(self):
        if self.fk_home_team.club.pc_id == settings.PC_CLUB_ID:
            return self.fk_away_team.club.name
        else:
            return self.fk_home_team.club.name

    def site_team(self):
        if self.fk_home_team.club.pc_id == settings.PC_CLUB_ID:
            return self.fk_home_team.name
        else:
            return self.fk_away_team.name

    def innings(self):
        innings = Inning.objects.filter(match_id=self.id)
        if innings:
            return sorted(innings, key=lambda a: a.get_inning_no())
        else:
            return []


# Inning Model
# Used for storing information about each inning in a match.
# x2 linked to match
class Inning(models.Model):
    # Foreign Keys
    match = models.ForeignKey('Match', on_delete=models.CASCADE)

    # Fields
    bat_team_id = models.CharField(max_length=8)
    bowl_team_id = models.CharField(max_length=8)
    runs = models.IntegerField()
    wickets = models.IntegerField()
    overs = models.FloatField()
    declared = models.BooleanField()
    extras_byes = models.IntegerField(default=0)
    extras_leg_byes = models.IntegerField(default=0)
    extras_wides = models.IntegerField(default=0)
    extras_no_balls = models.IntegerField(default=0)
    extras_penalties = models.IntegerField(default=0)
    extras_total = models.IntegerField(default=0)
    highlights = models.TextField(default='')
    complete_innings = models.BooleanField(default=False)

    def get_inning_no(self):
        if self.match.batted_first == self.bat_team_id:
            return 1
        else:
            return 2

    def bat_team_name(self):
        return PCTeam.objects.filter(pc_id=self.bat_team_id)[0].club.name

    def bowl_team_name(self):
        return 'This hasnt been implemented'


# Player Model
# Used to store information about each inning
class Player(models.Model):
    # Fields
    player_name = models.CharField(max_length=255)
    player_id = models.CharField(max_length=8)
    kvcc_player = models.BooleanField()

    # MVP Methods
    def get_mvp_scores(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]
    ):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
        ).aggregate(
            total=Sum('mvp_total'),
            bat=Sum((F('mvp_bat_runs') + F('mvp_bat_parscorebonus')) * 10),
            bowl=Sum((
                F('mvp_bowl_assisted') + F('mvp_bowl_unassisted') + F('mvp_bowl_economybonus')
            ) * 10),
            field=Sum((
                F('mvp_field_assisted') + F('mvp_field_unassisted')
            ) * 10),
        )

    def get_mvp_score(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets total mvp points for a given team and season '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season
        ).aggregate(Sum('mvp_total'))['mvp_total__sum']

    def bat_mvp_points(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets total number of batting mvp points for a given team and season '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
        ).aggregate(
            total=Sum((
                F('mvp_bat_runs') + F('mvp_bat_parscorebonus')
            ) * 10)
        )['total']

    def bowl_mvp_points(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets total number of bowling mvp points for a given team and season '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True,
        ).aggregate(
            total=Sum((
                F('mvp_bowl_assisted') + F('mvp_bowl_unassisted') + F('mvp_bowl_economybonus')
            ) * 10)
        )['total']

    def field_mvp_points(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets total number of field mvp points for a given team and season '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season
        ).aggregate(
            total=Sum((
                F('mvp_field_assisted') + F('mvp_field_unassisted')
            ) * 10)
        )['total']

    # Player Value Methods
    def get_value(
            self,
            season=[get_current_year()]):
        ''' Gets the players value '''
        try:
            return PlayerValue.objects.filter(
                player__id=self.id,
                season__in=season
            )[0].value
        except IndexError:
            return '-'

    def set_value(self):
        ''' Creates the players value '''
        values = [self.get_mvp_score([season]) for season in range(
            int(settings.PC_START_YEAR),
            date.today().year
        )[-3:]]
        values = [x for x in values if x is not None]
        if len(values) != 0:
            average = sum(values) / float(len(values))
            new_player_value = round(average / 100.0, 1)
            if new_player_value < 0.5:
                new_player_value = 0.5
            classification = self.get_classification()
            if classification != 'Unknown':
                player_value = PlayerValue(
                    season=get_current_year(),
                    value=new_player_value,
                    classification=classification
                )
                player_value.player_id = self.id
                player_value.save()
                return True
            return None
        return False

    # Classification Methods
    def percentage_bat_points(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        '''Gets the percentage for mvp points from batting '''
        bat = self.bat_mvp_points(season, teams) or 0
        bowl = self.bowl_mvp_points(season, teams) or 0
        try:
            return bat / float(bat + bowl) * 100
        except ZeroDivisionError:
            return '-'

    def get_classification(
            self,
            season=[get_current_year() - 2, get_current_year() - 1]):
        """ Calculates the players current classification for past two years """
        pbp = self.percentage_bat_points(season)
        if pbp != '-':
            if pbp >= 70:
                return 'Batsmen'
            elif pbp < 43:
                return 'Bowler'
            else:
                return 'All rounder'
        else:
            return 'Unknown'

    # Match Info Methods
    def played_game(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Checks if the player has played a game for a given team and season '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season
        ).count() != 0

    def get_games(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of games played by a player '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
        ).count()

    # Bowling Stats Methods
    def has_bowled(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Checks if player has bowled '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True,
        ).count() != 0

    def get_wickets(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of wickets taken '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True
        ).aggregate(Sum('bowl_wickets_total'))['bowl_wickets_total__sum']

    def get_overs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of overs bowled '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True
        ).aggregate(Sum('bowl_overs'))['bowl_overs__sum']

    def get_maidens(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of maiden overs bowled '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True
        ).aggregate(Sum('bowl_maidens'))['bowl_maidens__sum']

    def get_bowl_runs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets runs scored against bowler '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True
        ).aggregate(Sum('bowl_runs'))['bowl_runs__sum']

    def get_5_wickets(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of 5 wicket hauls '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bowl=True,
            bowl_wickets_total__gte=5,
        ).count()

    def get_economy(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets bowlers economy '''
        try:
            return self.get_bowl_runs(season, teams) / self.get_overs(season, teams)
        except:
            return '-'

    def get_bowl_average(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets bowlers average '''
        try:
            return self.get_bowl_runs(season, teams) / self.get_wickets(season, teams)
        except:
            return '-'

    # Batting Stats Methods
    def has_batted(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Checks if player has batted in given season and team '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
        ).count() != 0

    def get_runs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets runs scored by player '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
        ).aggregate(Sum('bat_runs'))['bat_runs__sum']

    def get_par_runs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets players par runs '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
        ).aggregate(Sum('bat_par_score'))['bat_par_score__sum']

    def get_innings(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of times player has batted '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
        ).count()

    def get_not_outs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of times player has been not out '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
            bat_how_out='no',
        ).count()

    def get_average(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets players batting average '''
        try:
            return float(self.get_runs(season, teams)) / float(
                self.get_innings(season, teams) - self.get_not_outs(season, teams)
            )
        except:
            return '-'

    def get_50s(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of times 50 runs have been scored '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
            bat_runs__range=[50, 99],
        ).count()

    def get_100s(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets number of times 100 runs have been scored '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            bat=True,
            bat_runs__gte=100,
        ).count()

    def get_high_score(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        ''' Gets players highest score '''
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
        ).aggregate(Max('bat_runs'))['bat_runs__max']

    # Fielding Stats Methods
    def get_catches(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season
        ).aggregate(Sum('field_catches'))['field_catches__sum']

    def get_fielding_catches(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            wicket_keeper=False
        ).aggregate(Sum('field_catches'))['field_catches__sum'] or 0

    def get_keeping_catches(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            wicket_keeper=True
        ).aggregate(Sum('field_catches'))['field_catches__sum'] or 0

    def get_stumpings(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            wicket_keeper=True
        ).aggregate(Sum('field_stumped'))['field_stumped__sum'] or 0

    def get_run_outs(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season
        ).aggregate(Sum('field_run_outs'))['field_run_outs__sum'] or 0

    def get_keeping_wickets(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            wicket_keeper=True
        ).aggregate(total=Sum(F('field_catches') + F('field_stumped')))['total'] or 0

    def get_fielding_wickets(
            self,
            season=[get_current_year()],
            teams=[v['id'] for k, v in settings.PC_TEAMS.iteritems()]):
        return Performance.objects.filter(
            Q(match__home_team_id__in=teams) | Q(match__away_team_id__in=teams),
            player__id=self.id,
            match__season__in=season,
            wicket_keeper=False
        ).aggregate(total=Sum(F('field_catches') + F('field_run_outs')))['total'] or 0


# Performance Model
# Is used for storing data about a players performance in a match
# xN linked to Player. N-number of matches player
# x22+unsure linked to Match
class Performance(models.Model):
    # Foreign Keys
    match = models.ForeignKey('Match', on_delete=models.CASCADE)
    player = models.ForeignKey('Player', on_delete=models.CASCADE)

    # Standard Fields
    captain = models.BooleanField(default=False)
    wicket_keeper = models.BooleanField(default=False)

    # Batting Performance Fields
    bat = models.BooleanField(default=False)
    bat_position = models.IntegerField(default=0)
    bat_runs = models.IntegerField(default=0)
    bat_par_score = models.IntegerField(default=0)
    bat_balls = models.IntegerField(default=0)
    bat_how_out = models.CharField(max_length=32, default='DNB')
    bat_out_bowler = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='bat_bowler',
        blank=True,
        null=True
    )
    bat_out_fielder = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='bat_fielder',
        blank=True,
        null=True
    )
    bat_inning_no = models.IntegerField(default=0)

    # Bowling Performance Fields
    bowl = models.BooleanField(default=False)
    bowl_overs = models.FloatField(default=0)
    bowl_runs = models.IntegerField(default=0)
    bowl_maidens = models.IntegerField(default=0)
    bowl_position = models.IntegerField(default=0)
    bowl_pareconomy = models.FloatField(default=0.0)
    bowl_wickets_lbw = models.IntegerField(default=0)
    bowl_wickets_bowled = models.IntegerField(default=0)
    bowl_wickets_stumped = models.IntegerField(default=0)
    bowl_wickets_caught = models.IntegerField(default=0)
    bowl_wickets_hit_wicket = models.IntegerField(default=0)
    bowl_wickets_total = models.IntegerField(default=0)
    bowl_inning_no = models.IntegerField(default=0)

    # Fielding Performance Fields
    field_catches = models.IntegerField(default=0)
    field_run_outs = models.IntegerField(default=0)
    field_stumped = models.IntegerField(default=0)

    # MVP Performance Fields
    mvp = models.BooleanField(default=False)
    mvp_total = models.FloatField(default=0.0)
    mvp_bat_runs = models.FloatField(default=0.0)
    mvp_bat_parscorebonus = models.FloatField(default=0.0)
    mvp_bowl_assisted = models.FloatField(default=0.0)
    mvp_bowl_unassisted = models.FloatField(default=0.0)
    mvp_bowl_economybonus = models.FloatField(default=0.0)
    mvp_field_assisted = models.FloatField(default=0.0)
    mvp_field_unassisted = models.FloatField(default=0.0)

    # Methods
    def overs_conversion(self, overs):
        ''' Converts overs in the form 6.3 (6 overs 3 balls) to 6.5 (6 1/2 overs)'''
        str_overs = str(overs)
        str_overs = str_overs.split('.')
        if len(str_overs) == 2:
            overs = float(str_overs[0]) + float(str_overs[1]) / 6.0
        else:
            overs = float(overs)
        return overs

    # MVP Methods
    def generate_mvp_scores(self):
        ''' Generate mvp score for performances '''
        if self.bat:
            self.mvp_bat_runs = self.bat_runs / 10.0
            parscorebonus = (self.bat_runs - self.bat_par_score) / 10.0
            if parscorebonus < 0 and self.bat_how_out == 'no':
                parscorebonus = 0
            self.mvp_bat_parscorebonus = parscorebonus
        if self.bowl:
            self.mvp_bowl_assisted = (self.bowl_wickets_caught + self.bowl_wickets_stumped) * 1.25
            self.mvp_bowl_unassisted = (
                self.bowl_wickets_lbw + self.bowl_wickets_bowled + self.bowl_wickets_hit_wicket
            ) * 2.5
            self.mvp_bowl_economybonus = -((
                self.bowl_runs / self.overs_conversion(
                    self.bowl_overs if self.bowl_overs != 0 else 1
                )
            ) - self.bowl_pareconomy) / 10.0
        self.mvp_field_assisted = (self.field_catches + self.field_stumped) * 1.25
        self.mvp_field_unassisted = (self.field_run_outs) * 2.5
        self.mvp = True
        self.mvp_total = int((
            self.mvp_bat_runs + self.mvp_bat_parscorebonus + self.mvp_bowl_assisted +
            self.mvp_bowl_unassisted + self.mvp_bowl_economybonus + self.mvp_field_assisted +
            self.mvp_field_unassisted
        ) * 10)
        self.save()

    # Methods
    def how_out_descriptive(self):
        ''' Returns a descriptive how out definition '''
        if self.bat_how_out in ['b', 'lbw']:
            return ''
        elif self.bat_how_out in ['ct', 'ro', 'st']:
            return self.bat_how_out + ' ' + self.bat_out_fielder.player_name
        elif self.bat_how_out == 'no':
            return 'Not Out'


# Team Model
# Used for storing data about each fantasy team
# xN linked to user. N-number of seasons team played
class Team(models.Model):
    # Foreign Keys
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='backup_team_user'
    )

    # Fields
    team_name = models.CharField(max_length=255, default='Choose your team name')
    season = models.IntegerField(default=get_current_year)
    penalties = models.IntegerField(default=0)

    stripe_payment_token = models.TextField(default='')

    # Value Methods
    def current_value(self):
        return sum(
            PlayerValue.objects.filter(
                player__id=player.player.id,
                season=self.season
            )[0].value for player in self.current_players()
        )

    # MVP Points methods
    def get_points(self):
        ''' Gets the total team points '''
        return sum([i.get_points() for i in self.all_players()]) - self.penalties

    def last_week_points(self):
        ''' Gets the total team points last week '''
        players = self.all_players()
        today = date.today()
        sunday = today - timedelta(7 + (today.weekday() + 1) % 7)
        monday = sunday - timedelta(6)
        return sum([i.get_points([monday, sunday]) for i in players])

    # Player Methods
    def all_players(self):
        ''' Gets all the players that have been in the team '''
        return TeamPlayer.objects.filter(team__id=self.id)

    def current_players(self):
        ''' Gets all the players currently in the team '''
        return TeamPlayer.objects.filter(
            team__id=self.id,
            date_deactive=None,
        )

    def high_scores(self, last_week=True, all_time=True):
        ''' Gets points high scores '''
        high_scores = {
            'all_time': None,
            'last_week': None,
        }
        players = self.all_players()
        if all_time:
            try:
                best_player = max(
                    players,
                    key=lambda a: a.get_points()
                )
                points = best_player.get_points()
            except ValueError:
                points = 0
            if points == 0:
                high_scores['all_time'] = None
            else:
                high_scores['all_time'] = {
                    'name': best_player.player.player_name,
                    'points': points,
                }
        if last_week:
            today = date.today()
            sunday = today - timedelta(7 + (today.weekday() + 1) % 7)
            monday = sunday - timedelta(6)
            try:
                best_player = max(
                    players,
                    key=lambda a: a.get_points([monday, sunday]),
                )
                points = best_player.get_points([monday, sunday])
            except ValueError:
                points = 0
            if points == 0:
                high_scores['last_week'] = None
            else:
                high_scores['last_week'] = {
                    'name': best_player.player.player_name,
                    'points': points,
                }
        return high_scores

    def get_captain(self):
        try:
            return self.current_players().filter(captain=True)[0]
        except:
            return None

    def add_player(self, player_id, captain=False):
        if len(self.current_players()) < 11:
            player = TeamPlayer(
                team_id=self.id,
                player_id=player_id,
                captain=captain,
            )
            player.save()

    def remove_player(self, player_id):
        player = self.current_players().filter(player__id=player_id)[0]
        player.deactivate()
        if player.date_active == player.date_deactive:
            player.delete()

    def change_captain(self, captain_id):
        current_captain = self.get_captain()
        new_captain = self.current_players().filter(player__id=captain_id)[0]
        if current_captain is not None:
            self.remove_player(current_captain.player.id)
            self.add_player(current_captain.player.id)
        self.remove_player(new_captain.player.id)
        self.add_player(new_captain.player.id, captain=True)

    def get_url(self):
        return reverse('fantasyleague:user_team', args=[self.id])

    def get_absolute_url(self):
        return reverse('fantasyleague:user_team', kwargs={'team_id': self.id})


# TeamPlayer Model
# Used for storing data about each player in a fantasy team
class TeamPlayer(models.Model):
    # Foreign Keys
    team = models.ForeignKey(
        'Team',
        on_delete=models.CASCADE,
        related_name='backup_teamplayer_team'
    )
    player = models.ForeignKey(
        'Player',
        on_delete=models.CASCADE,
        related_name='backup_teamplayer_player'
    )

    # Fields
    captain = models.BooleanField(default=False)
    date_active = models.DateField(default=timezone.now)
    # On this date they will appear in the team
    date_deactive = models.DateField(null=True, blank=True)
    # On this date they will beremoved from team

    # Methods
    def get_points(self, date_range=None):
        ''' This function gets the points of the player in the given date range '''
        if date_range is None:
            date_range = [
                self.date_active,
                self.date_deactive if self.date_deactive is not None else date.today()
            ]
        # Check date range is not outside of time when player in team
        # If it is correct date range
        if date_range[0] < self.date_active:
            date_range[0] = self.date_active
        if date_range[1] > (
                self.date_deactive if self.date_deactive is not None else date.today()
        ):
            date_range[1] = self.date_deactive
        # Gets points in date_range
        points = Performance.objects.filter(
            player__id=self.player.id,
            match__match_date__range=date_range,
            mvp=True,
        ).aggregate(Sum('mvp_total'))['mvp_total__sum'] or 0
        # Corrects points if player is captain
        return points * 2 if self.captain else points

    def is_active(self):
        ''' Checks if a player is active '''
        today = date.today()
        # Gets day TeamPlayer will be deactivated
        deactive = self.date_deactive if self.date_deactive is not None else (
            date.today() + timedelta(days=1)
        )
        return self.date_active <= today and today < deactive

    def make_captain(self):
        """ Sets captain status to true """
        self.captain = True  # Add captain status
        self.save()

    def de_captain(self):
        """ Sets captain status to false """
        self.captain = False  # Remove captain status
        self.save()

    def deactivate(self):
        """ Deactivates player. ie removes from team """
        self.date_deactive = date.today()  # Set de_active date
        self.save()


# Player Value Model
# Used for storing data about each players value in the fantasy league
class PlayerValue(models.Model):
    # Foreign Keys
    player = models.ForeignKey(
        'Player',
        related_name='backup_playervalue_player'
    )

    # Fields
    season = models.IntegerField(default=get_current_year)
    value = models.FloatField(default=0)
    classification = models.CharField(max_length=32)
    active = models.BooleanField(default=True)


# BattingParScores Model
# Used for storing the batting par scores
class BattingParScores(models.Model):
    # Fields
    bat_position = models.IntegerField(default=0)
    average_score = models.FloatField(default=0)
    season = models.IntegerField(default=get_current_year)


# Activaton Code model
# Used for storing email activation codes when user registers
class ActivationCode(models.Model):
    # Foreign Keys
    user = models.OneToOneField(User)

    # Fields
    activation_code = models.CharField(max_length=255)


class PlayCricketTeam(models.Model):
    team_id = models.CharField(max_length=8, blank=False)
    team_name = models.CharField(max_length=64, blank=False)
    first_season = models.CharField(max_length=4, blank=False)
    fantasy_league = models.BooleanField(default=False, blank=False)
    active = models.BooleanField(default=True, blank=False)
    match_results = models.BooleanField(default=False, blank=True)

    def deactivate(self):
        self.active = False
        self.save()

    def __str__(self):
        return self.team_name
