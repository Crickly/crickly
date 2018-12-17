# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cricket.views.match.generic import View as BaseView
from cricket.views.match.index import View as Index
from cricket.views.match.fixtures import View as Fixtures
from cricket.views.match.results import View as Results
from cricket.views.match.match import View as Match


__all__ = [
    'BaseView',
    'Index',
    'Fixtures', 'Results',
    'Match',
]
