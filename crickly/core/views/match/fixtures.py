# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
# -- none


# Django imports
from django.shortcuts import render


# Project imports
from crickly.core.views.match import BaseView


class View(BaseView):
    def get(self, request):
        self.clear_context()
        self.add_context(
            'matches',
            self.get_fixtures()
        )
        return render(
            request,
            'crickly/matches/fixtures.html',
            context=self.get_context()
        )
