# -*- coding: utf-8 -*-
from django.contrib import admin

from crickly.core.models import (Match, Inning, Umpire, UmpireAssignment, Competition,
                            Ground, Club, Team, Player, Performance, BatPerformance,
                            BowlPerformance, FieldPerformance, MatchDate,
                            Scorer, ScorerAssignment, League)


admin.site.register(Match)
admin.site.register(Inning)
admin.site.register(Umpire)
admin.site.register(UmpireAssignment)
admin.site.register(Scorer)
admin.site.register(ScorerAssignment)
admin.site.register(Competition)
admin.site.register(League)
admin.site.register(Ground)
admin.site.register(Club)
admin.site.register(Team)
admin.site.register(Player)
admin.site.register(Performance)
admin.site.register(BatPerformance)
admin.site.register(BowlPerformance)
admin.site.register(FieldPerformance)
admin.site.register(MatchDate)

# Play Cricket stuff below...

# from crickly.models import PlayCricketTeam


# @admin.register(PlayCricketTeam)
# class PlayCricketTeamAdmin(admin.ModelAdmin):
#     exclude = ('active',)
#     fieldsets = (
#         (None, {
#             'fields': ('team_id', 'team_name')
#         }),
#         ('Advanced Options', {
#             'classes': ('collapse',),
#             'fields': ('first_season', 'fantasy_league', 'match_results'),
#         })
#     )
#     list_display = ('team_name',)
#     list_filter = ('active',)
