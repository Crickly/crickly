# -*- coding: utf-8 -*-
from __future__ import unicode_literals


class AbstractFunctionError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class AbstractClassError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class kwargError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class validateFunctionNotCallable(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class notEnoughInningsError(Exception):
    def __init(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)
