# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from cricket.core.views.match.generic import View as BaseView
from cricket.core.views.match.index import View as Index
from cricket.core.views.match.fixtures import View as Fixtures
from cricket.core.views.match.results import View as Results
from cricket.core.views.match.match import View as Match


__all__ = [
    'BaseView',
    'Index',
    'Fixtures', 'Results',
    'Match',
]
