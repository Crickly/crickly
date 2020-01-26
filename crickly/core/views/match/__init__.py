# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from crickly.core.views.match.generic import View as BaseView
from crickly.core.views.match.index import View as Index
from crickly.core.views.match.fixtures import View as Fixtures
from crickly.core.views.match.results import View as Results
from crickly.core.views.match.match import View as Match


__all__ = [
    'BaseView',
    'Index',
    'Fixtures', 'Results',
    'Match',
]
