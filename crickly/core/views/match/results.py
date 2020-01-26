# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
from datetime import date


# Django imports
from django.shortcuts import render


# Project imports
from crickly.core.views.match import BaseView


class View(BaseView):
    def get_start_of_month(self):
        today = self.get_date()
        return date(today.year, today.month, 1)

    def get(self, request):
        self.clear_context()
        self.add_context(
            'matches',
            self.get_results(
                date__date__range=[
                    self.get_start_of_month(),
                    self.get_date()
                ]
            )
        )
        self.add_context(
            'seasons',
            self.get_seasons()
        )
        self.add_context(
            'current_month',
            self.get_date().strftime('%m')
        )
        self.add_context(
            'months',
            [
                {'name': 'all', 'value': '00'},
                {'name': 'January', 'value': '01'},
                {'name': 'February', 'value': '02'},
                {'name': 'March', 'value': '03'},
                {'name': 'April', 'value': '04'},
                {'name': 'May', 'value': '05'},
                {'name': 'June', 'value': '06'},
                {'name': 'July', 'value': '07'},
                {'name': 'August', 'value': '08'},
                {'name': 'September', 'value': '09'},
                {'name': 'October', 'value': '10'},
                {'name': 'November', 'value': '11'},
                {'name': 'December', 'value': '12'},
            ]
        )
        return render(
            request,
            'crickly/matches/results.html',
            context=self.get_context()
        )
