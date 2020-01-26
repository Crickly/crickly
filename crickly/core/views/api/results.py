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
    def validate_year(self, year):
        if int(year) not in range(2010, date.today().year + 1):
            raise kwargError('Year not in range (2010 - {})'.format(date.today().year))

    def validate_month(self, month):
        if int(month) not in range(0, 13):
            raise kwargError('Month not in range (00 - 12)')

    def get_start_end_date(self):
        month = int(self.get_kwarg('month', date.today().month))
        year = int(self.get_kwarg('year', date.today().year))
        today = date.today()

        if month == 0:
            start = date(year, 1, 1)
            end = date(year, 12, 31)
        elif today.year == year and today.month == month:
            start = date(year, month, 1)
            end = today
        else:
            start = date(year, month, 1)
            if month == 12:
                end = date(year, month, 31)
            else:
                end = date(year, month + 1, day=1) - timedelta(days=1)

        return start, end

    def get(self, request, **kwargs):
        try:
            self.validate_kwargs()

            # Get current and end date
            start, end = self.get_start_end_date()

            # Get matches in date range
            matches = Match.objects.filter(
                date__date__range=[start, end]
            ).order_by('-date__date')

            # Get important info
            important_info = [{
                'match_date': i.date.date.strftime('%d.%m'),
                'home_club_name': i.home_team.club.name,
                'home_team_name': i.home_team.name,
                'away_club_name': i.away_team.club.name,
                'away_team_name': i.away_team.name,
                'result_description': i.result_description,
                'id': i.id,
            } for i in matches]

            return self.JsonResponse(
                {
                    'matches': important_info,
                    'kwargs': self.kwargs,
                }
            )
        except kwargError as e:
            return self.error_message(str(e))
        except:
            return self.error_message()
