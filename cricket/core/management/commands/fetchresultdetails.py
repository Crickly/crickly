# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.core.management.base import BaseCommand
from django.conf import settings
from cricket.models import Match, Inning, Player, Performance, BattingParScores
from Queue import Queue
from threading import Thread
from datetime import date, timedelta
import requests
import json


class Command(BaseCommand):
    help = 'will attempt to fetch the results data for matches with full_scorecard=False'
    API_URL = 'http://www.play-cricket.com/api/v2/'
    queue = Queue(maxsize=0)
    no_basic_uploads = 0
    no_full_uploads = 0
    no_innings_uploads = 0
    no_player_uploads = 0
    no_performance_uploads = 0
    no_not_uploaded = 0

    def get_data(self, url):
        r = requests.get(
            self.API_URL + url + '&api_token={}'.format(settings.PC_API_KEY)
        )
        if r.ok:
            return json.loads(r.content)
        else:
            r.raise_for_status()

    def is_innings_basic_data(self, innings):
        return len(innings['bat']) == 0 or len(innings['bowl']) == 0

    def getParScores(self, no_batsmen, match_score):
        average_match_total = 0
        average_scores = {}
        for i in range(1, no_batsmen + 1):
            average_scores[i] = BattingParScores.objects.filter(bat_position=i)[0].average_score
            average_match_total += average_scores[i]
        parScores = {}
        for i in range(1, no_batsmen + 1):
            parScores[i] = (average_scores[i] / average_match_total) * match_score
        return parScores

    def zero_if_empty(self, value):
        return value if value != '' else 0

    def update_inning(self, match, inning, saved_inning, complete):
        if match.fk_home_team.pc_id == inning['team_batting_id']:
            bowl_team_id = match.fk_away_team.pc_id
        else:
            bowl_team_id = match.fk_home_team.pc_id
        saved_inning.bat_team_id = inning['team_batting_id']
        saved_inning.bowl_team_id = bowl_team_id
        saved_inning.runs = self.zero_if_empty(inning['runs'])
        saved_inning.wickets = self.zero_if_empty(inning['wickets'])
        saved_inning.overs = self.zero_if_empty(inning['overs'])
        saved_inning.declared = inning['declared']
        saved_inning.extras_byes = self.zero_if_empty(inning['extra_byes'])
        saved_inning.extras_leg_byes = self.zero_if_empty(inning['extra_leg_byes'])
        saved_inning.extras_wides = self.zero_if_empty(inning['extra_wides'])
        saved_inning.extras_no_balls = self.zero_if_empty(inning['extra_no_balls'])
        saved_inning.extras_penalties = self.zero_if_empty(inning['extra_penalty_runs'])
        saved_inning.extras_total = self.zero_if_empty(inning['total_extras'])
        saved_inning.complete_innings = complete
        saved_inning.save()

    def process(self, item):
        try:
            num_unsures = 1
            id = item[0]
            match = Match.objects.filter(id=id)[0]
            match_data = self.get_data(
                'match_detail.json?match_id={}'.format(match.match_id)
            )['match_details'][0]
            if match.match_id == str(match_data['id']):
                # check for innings in match data
                if match_data['result'] not in ['A', 'C', 'CON']:
                    try:
                        basic_info = self.is_innings_basic_data(
                            match_data['innings'][0]
                        ) or self.is_innings_basic_data(match_data['innings'][1])
                    except IndexError:
                        basic_info = True
                    if basic_info and not match.is_live_score():
                        # upload basic info
                        inning_no = Inning.objects.filter(match__id=match.id).count()
                        if inning_no == 2:
                            pass  # ############################ TODO
                        elif inning_no == 0:
                            for i in match_data['innings']:
                                if match.fk_home_team.pc_id == i['team_batting_id']:
                                    bowl_team_id = match.fk_away_team.pc_id
                                else:
                                    bowl_team_id = match.fk_home_team.pc_id
                                inningargs = {
                                    'bat_team_id': i['team_batting_id'],
                                    'bowl_team_id': bowl_team_id,
                                    'runs': i['runs'] if i['runs'] != '' else 0,
                                    'wickets': i['wickets'] if i['wickets'] != '' else 0,
                                    'overs': i['overs'] if i['overs'] != '' else 0,
                                    'declared': i['declared'],
                                }
                                inning = Inning(**inningargs)
                                inning.match_id = match.id
                                inning.save()
                                self.no_innings_uploads += 1
                        elif inning_no == 1:
                            pass  # ######################## TODO

                        self.no_basic_uploads += 1
                        if match.fk_date.get_date() < date.today() - timedelta(days=14):
                            match.processing_issue = True
                    else:
                        # full results upload
                        # check if two basic innings exist
                        saved_innings = Inning.objects.filter(match__id=match.id)
                        if saved_innings.count() == 2:
                            # two innings exist so add to innings
                            for i in match_data['innings']:
                                inning = None
                                for saved_inning in saved_innings:
                                    if saved_inning.bat_team_id == i['team_batting_id']:
                                        inning = saved_inning
                                        break
                                if inning is None:
                                    raise Exception
                                # Check importance of complete_innings=True TODO
                                self.update_inning(match, i, inning, True)

                        elif saved_innings.count() == 1:
                            # Work out which inning exists and update it.
                            # Then add new inning (if exists).
                            saved_inning = saved_innings[0]
                            if len(match_data['innings']) == 1:
                                self.update_inning(
                                    match,
                                    match_data['innings'][0],
                                    saved_inning,
                                    True
                                )
                            elif len(match_data['innings']) == 2:
                                if match_data['innings'][0][
                                        'team_batting_id'
                                ] == saved_inning.bat_team_id:
                                    self.update_inning(
                                        match,
                                        match_data['innings'][0],
                                        saved_inning,
                                        True
                                    )
                                    unsaved_inning = match_data['innings'][1]
                                else:
                                    self.update_inning(
                                        match,
                                        match_data['innings'][1],
                                        saved_inning,
                                        True
                                    )
                                    unsaved_inning = match_data['innings'][0]

                                # Save unsaved inning.
                                if match.fk_home_team.pc_id == unsaved_inning[
                                    'team_batting_id'
                                ]:
                                    bowl_team_id = match.fk_away_team.pc_id
                                else:
                                    bowl_team_id = match.fk_home_team.pc_id

                                inningargs = {
                                    'bat_team_id': unsaved_inning['team_batting_id'],
                                    'bowl_team_id': bowl_team_id,
                                    'runs': self.zero_if_empty(
                                        unsaved_inning['runs']
                                    ),
                                    'wickets': self.zero_if_empty(
                                        unsaved_inning['wickets']
                                    ),
                                    'overs': self.zero_if_empty(
                                        unsaved_inning['overs']
                                    ),
                                    'declared': unsaved_inning['declared'],
                                    'extras_byes': self.zero_if_empty(
                                        unsaved_inning['extra_byes']
                                    ),
                                    'extras_leg_byes': self.zero_if_empty(
                                        unsaved_inning['extra_leg_byes']
                                    ),
                                    'extras_wides': self.zero_if_empty(
                                        unsaved_inning['extra_wides']
                                    ),
                                    'extras_no_balls': self.zero_if_empty(
                                        unsaved_inning['extra_no_balls']
                                    ),
                                    'extras_penalties': self.zero_if_empty(
                                        unsaved_inning['extra_penalty_runs']
                                    ),
                                    'extras_total': self.zero_if_empty(
                                        unsaved_inning['total_extras']
                                    ),
                                    'complete_innings': True,
                                }
                                inning = Inning(**inningargs)
                                inning.match_id = match.id
                                inning.save()
                                self.no_innings_uploads += 1

                        else:
                            # create two new full innings
                            for i in match_data['innings']:
                                if match.fk_home_team.pc_id == i['team_batting_id']:
                                    bowl_team_id = match.fk_away_team.pc_id
                                else:
                                    bowl_team_id = match.fk_home_team.pc_id
                                inningargs = {
                                    'bat_team_id': i['team_batting_id'],
                                    'bowl_team_id': bowl_team_id,
                                    'runs': i['runs'] if i['runs'] != '' else 0,
                                    'wickets': i['wickets'] if i['wickets'] != '' else 0,
                                    'overs': i['overs'] if i['overs'] != '' else 0,
                                    'declared': i['declared'],
                                    'extras_byes': i['extra_byes'] if i['extra_byes'] != '' else 0,
                                    'extras_leg_byes': i['extra_leg_byes'] if i['extra_leg_byes'] != '' else 0,
                                    'extras_wides': i['extra_wides'] if i['extra_wides'] != '' else 0,
                                    'extras_no_balls': i['extra_no_balls'] if i['extra_no_balls'] != '' else 0,
                                    'extras_penalties': i['extra_penalty_runs'] if i['extra_penalty_runs'] != '' else 0,
                                    'extras_total': i['total_extras'] if i['total_extras'] != '' else 0,
                                    'complete_innings': True,
                                }
                                inning = Inning(**inningargs)
                                inning.match_id = match.id
                                inning.save()
                                self.no_innings_uploads += 1

                        # FOR EACH PLAYER CHECK DB to see if a performance already,
                        # exists for a player in that match if it does add to performances

                        # Add all the players and create performances
                        performances = {}
                        saved_performances = Performance.objects.filter(match_id=match.id)
                        unsure_performances = saved_performances.filter(player_id=1)
                        unsure_performances.delete()
                        kvcc_home = False
                        if match_data['home_club_id'] == settings.PC_CLUB_ID:  # check if kvcc is the home team
                            kvcc_home = True
                        for team in match_data['players']:
                            for k, team in team.iteritems():
                                is_team_kvcc = False
                                if k == 'home_team' and kvcc_home:
                                    is_team_kvcc = True
                                elif k == 'away_team' and not kvcc_home:
                                    is_team_kvcc = True
                                for eachplayer in team:
                                    # check if player already exists
                                    if Player.objects.filter(
                                            player_id=eachplayer[
                                                'player_id'
                                            ] if eachplayer['player_id'] is not None else 0,
                                            kvcc_player=is_team_kvcc if eachplayer[
                                                'player_id'
                                            ] is not None else False,
                                    ).count() == 0:
                                        # Create player in db
                                        playerargs = {
                                            'player_name': eachplayer['player_name'],
                                            'player_id': eachplayer[
                                                'player_id'
                                            ] if eachplayer['player_id'] is not None else 0,
                                            'kvcc_player': is_team_kvcc,
                                        }
                                        player = Player(**playerargs)
                                        self.no_player_uploads += 1
                                        player.save()
                                    else:
                                        # Fetch current player from db
                                        player = Player.objects.filter(
                                            player_id=eachplayer[
                                                'player_id'
                                            ] if eachplayer['player_id'] is not None else 0,
                                            kvcc_player=is_team_kvcc if eachplayer[
                                                'player_id'
                                            ] is not None else False,
                                        )[0]

                                    player_performances = saved_performances.filter(
                                        player_id=player.id
                                    )

                                    if player_performances.count() == 1:
                                        performance = player_performances[0]
                                        performance.captain = eachplayer['captain']
                                        performance.wicket_keeper = eachplayer[
                                            'wicket_keeper'
                                        ]

                                        # Reset stats.
                                        performance.bowl_wickets_lbw = 0
                                        performance.bowl_wickets_bowled = 0
                                        performance.bowl_wickets_stumped = 0
                                        performance.bowl_wickets_caught = 0
                                        performance.bowl_wickets_hit_wicket = 0

                                        performance.field_catches = 0
                                        performance.field_run_outs = 0
                                        performance.field_stumped = 0

                                        performance.mvp = False
                                    else:
                                        performanceargs = {
                                            'captain': eachplayer['captain'],
                                            'wicket_keeper': eachplayer['wicket_keeper'],
                                        }
                                        # create performance for each player
                                        performance = Performance(**performanceargs)
                                        performance.match_id = match.id
                                        performance.player_id = player.id
                                        # Add Performance to performances dict with player_id as key

                                    performances[
                                        str(eachplayer[
                                            'player_id'
                                        ] if eachplayer['player_id'] is not None else '0_0')
                                    ] = performance
                        # add performance for unsure if it doesn't exist
                        if '0_0' not in performances.keys():
                            performances['0_0'] = Performance(
                                match_id=match.id,
                                player_id=1
                            )
                        # process match details to add to performances
                        try:
                            inning_no = 0
                            for inning in match_data['innings']:
                                inning_no += 1
                                total_runs = 0
                                # Add batting data to performances
                                no_batsmen = 0
                                for bat in inning['bat']:
                                    if bat['how_out'] != 'did not bat':
                                        no_batsmen += 1
                                        total_runs += int(bat['runs'] if bat['runs'] != '' else 0)
                                parScores = self.getParScores(no_batsmen, total_runs)
                                bat_number = 0
                                for bat in inning['bat']:
                                    if bat['batsman_id'] == '':  # check is batsman is unsure
                                        for i in range(num_unsures):
                                            bp = performances['0_' + str(i)]
                                            if not bp.bat:
                                                break  # available performance has been found to enter details
                                            elif i == num_unsures - 1:
                                                # must create new performance as none can be found
                                                num_unsures += 1
                                                bp = Performance(
                                                    match_id=match.id,
                                                    player_id=1
                                                )
                                                performances[
                                                    '0_' + str(i + 1)
                                                ] = bp
                                                break
                                    else:
                                        bp = performances[bat['batsman_id']]
                                    bp.bat_position = int(bat['position'])
                                    bp.bat_inning_no = inning_no
                                    # Add how out info
                                    if bat['how_out'] in ['lbw', 'b']:
                                        # batsman was out bowled or lbw
                                        bp.bat_how_out = bat['how_out']
                                        bowler = performances[
                                            bat['bowler_id'] if bat['bowler_id'] != '' else '0_0'
                                        ]
                                        bp.bat_out_bowler_id = bowler.player_id
                                        bp.bat_out_fielder_id = None
                                        if bat['how_out'] == 'b':
                                            bowler.bowl_wickets_bowled += 1
                                        else:
                                            bowler.bowl_wickets_lbw += 1
                                    elif bat['how_out'] == 'ro':
                                        bp.bat_how_out = bat['how_out']
                                        fielder = performances[
                                            bat['fielder_id'] if bat['fielder_id'] != '' else '0_0'
                                        ]
                                        bp.bat_out_bowler_id = None
                                        bp.bat_out_fielder_id = fielder.player_id
                                        fielder.field_run_outs += 1
                                    elif bat['how_out'] in ['ct', 'st']:
                                        bp.bat_how_out = bat['how_out']
                                        bowler = performances[
                                            bat['bowler_id'] if bat['bowler_id'] != '' else '0_0'
                                        ]
                                        fielder = performances[
                                            bat['fielder_id'] if bat['fielder_id'] != '' else '0_0'
                                        ]
                                        bp.bat_out_bowler_id = bowler.player_id
                                        bp.bat_out_fielder_id = fielder.player_id
                                        if bat['how_out'] == 'ct':
                                            bowler.bowl_wickets_caught += 1
                                            fielder.field_catches += 1
                                        else:
                                            bowler.bowl_wickets_stumped += 1
                                            fielder.field_stumped += 1
                                    elif bat['how_out'] == 'no':
                                        bp.bat_how_out = bat['how_out']
                                        bp.bat_out_bowler_id = None
                                        bp.bat_out_fielder_id = None
                                    # Add extra bat info
                                    if bat['how_out'] != 'did not bat':
                                        bp.bat = True
                                        bat_number += 1
                                        bp.bat_runs = bat['runs'] if bat['runs'] != '' else 0
                                        # bp.fours = bat['fours'] if bat['fours'] != '' else 0
                                        # bp.sixes = bat['sixes'] if bat['sixes'] != '' else 0
                                        bp.bat_balls = bat['balls'] if bat['balls'] != '' else 0
                                        bp.bat_par_score = parScores[bat_number]
                                # Add boling figures to performances
                                bowl_position = 0
                                # Calculate par economy
                                try:
                                    bowl_pareconomy = int(inning['runs']) / Performance().overs_conversion(
                                        inning['overs']
                                    )
                                except ZeroDivisionError:
                                    bowl_pareconomy = 0
                                for bowl in inning['bowl']:
                                    bowl_position += 1
                                    # Fix for multiple unsure players
                                    if bowl['bowler_id'] == '':
                                        for i in range(num_unsures):
                                            bp = performances['0_' + str(i)]
                                            if not bp.bowl:
                                                break
                                            elif i == num_unsures - 1:
                                                num_unsures += 1
                                                bp = Performance(
                                                    match_id=match.id,
                                                    player_id=1
                                                )
                                                performances['0_' + str(i + 1)] = bp
                                                break
                                    else:
                                        bp = performances[
                                            bowl['bowler_id'] if bowl['bowler_id'] != '' else '0'
                                        ]
                                    # Add bowloing info to performances
                                    bp.bowl_position = bowl_position
                                    bp.bowl_overs = bowl['overs'] if bowl['overs'] != '' else 0
                                    bp.bowl_runs = bowl['runs'] if bowl['runs'] != '' else 0
                                    bp.bowl_maidens = bowl['maidens'] if bowl['maidens'] != '' else 0
                                    bp.bowl_wickets_total = bowl['wickets'] if bowl['wickets'] != '' else 0
                                    bp.bowl_pareconomy = bowl_pareconomy
                                    bp.bowl = True
                                    bp.bowl_inning_no = inning_no
                        except KeyError:
                            match.processing_issue = True
                            self.stdout.write('Issue processing match {}'.format(match.match_id))
                        else:
                            # save all the performances
                            for k, v in performances.iteritems():
                                self.no_performance_uploads += 1
                                v.save()
                            # Save match
                            if not match.is_live_score():
                                match.full_scorecard = True
                            match.save()
                            self.no_full_uploads += 1
                        match.save()
                else:
                    self.no_not_uploaded += 1
                    # Check if match was played or not
                    if match_data[
                            'result'
                    ] in ['A', 'C', 'CON']:
                        # Not played
                        match.full_scorecard = True
                        match.save()
                        self.stdout.write(
                            'Match {} was not played so not uploading'.format(match.match_id)
                        )
                    elif match_data['result'] == 'M':
                        self.stdout.write('Match {} in progress'.format(match.match_id))
                    else:
                        # Match played
                        self.stdout.write('Match {} Does not have 2 innings'.format(match.match_id))
            else:
                self.no_not_uploaded += 1
                self.stdout.write('Issue fetching match {}'.format(match.match_id))
        except IOError:
            try:
                self.stdout.write('Error processing match {}'.format(match.match_id))
                match.processing_issue = True
                match.save()
            except:
                self.stdout.write('Errorprocessing match{}')

    def createWorkers(self):
        """ Create Workers/Threads """
        for i in range(1):
            worker = Thread(target=self.fetchResults)
            worker.start()

    def handle(self, *args, **options):
        """ Default command handler """
        for match in Match.objects.filter(
                full_scorecard=False,
                processing_issue=False,
                fk_team__match_results=True
        ):
            # will loop every match that does not have a full scorecard
            if match.fk_date.get_date() <= date.today():
                self.process([match.id, match.fk_team.id])
                # self.queue.put([match.id, match.fk_team.id])
        # self.createWorkers()
        # self.queue.join()
        # Debug info
        self.stdout.write('{} Basic match info has been uploaded'.format(self.no_basic_uploads))
        self.stdout.write('{} Full match info has been uploaded'.format(self.no_full_uploads))
        self.stdout.write('{} Players have been uploaded'.format(self.no_player_uploads))
        self.stdout.write('{} Innings have been uploaded'.format(self.no_innings_uploads))
        self.stdout.write('{} Performances have been uploaded'.format(self.no_performance_uploads))
        self.stdout.write('{} Matches not uploaded'.format(self.no_not_uploaded))
