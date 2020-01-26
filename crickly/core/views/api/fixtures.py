# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
# --None

# Python imports
from datetime import date, timedelta

# Project imports
from crickly.core.models import Match
from crickly.core.views.api import BaseView
from crickly.core.views.exceptions import kwargError


class View(BaseView):
    '''
        A view with creates a JSONResponse containing fixtures in the given period:
        wk - week
        mth - month
        sn - season ( defined to finish on 31st December )
    '''

    def validate_period(self, period):
        if period not in ['wk', 'mth', 'sn']:
            raise kwargError('Not a valid time period (wk/mth/sn)')

    def get_end_date(self):
        current_date = date.today()
        period = self.get_kwarg('period', 'wk')
        if period == 'wk':
            return current_date + timedelta(days=7)
        elif period == 'mth':
            return current_date + timedelta(days=31)
        elif period == 'sn':
            return date(current_date.year, 12, 31)

    def get(self, request, **kwargs):
        try:
            self.validate_kwargs()
            # Get current and end date
            current_date = date.today()
            end_date = self.get_end_date()

            # Get matches in date range
            matches = Match.objects.filter(
                date__date__range=[current_date, end_date]
            ).order_by('date__date')

            # Get important info
            important_info = [{
                'match_date': i.date.date.strftime('%d.%m'),
                'home_club_name': i.home_team.club.name,
                'home_team_name': i.home_team.name,
                'away_club_name': i.away_team.club.name,
                'away_team_name': i.away_team.name,
                'id': i.id,
            } for i in matches]

            return self.JsonResponse(
                {
                    'matches': important_info,
                }
            )
        except kwargError as e:
            return self.error_message(str(e))
        except:
            return self.error_message()
