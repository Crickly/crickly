# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
# -- None


# Django imports
from django.shortcuts import render


# Project imports
from crickly.core.views.match import BaseView


class View(BaseView):
    def get(self, request):
        self.clear_context()
        self.add_context(
            'recent_matches',
            self.get_results(
                date__date__lt=self.get_date()
            )[:5]
        )
        self.add_context(
            'upcoming_matches',
            self.get_fixtures()
        )

        return render(
            request,
            'crickly/matches/index.html',
            context=self.get_context()
        )
