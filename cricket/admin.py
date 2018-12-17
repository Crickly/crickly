#-*- coding: utf-8 -*-
from django.contrib import admin

from cricket.models import PlayCricketTeam


@admin.register(PlayCricketTeam)
class PlayCricketTeamAdmin(admin.ModelAdmin):
    exclude = ('active',)
    fieldsets = (
        (None, {
            'fields': ('team_id', 'team_name')
        }),
        ('Advanced Options', {
            'classes': ('collapse',),
            'fields': ('first_season', 'fantasy_league', 'match_results'),
        })
    )
    list_display = ('team_name',)
    list_filter = ('active',)
