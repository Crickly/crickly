# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
# --None


# Django imports
from django.views.generic import View as V


# Project imports
from crickly.core.views.exceptions import validateFunctionNotCallable


class View(V):
    '''
        A Generic view used by all API views
    '''
    context = {}

    def __init__(self, **kwargs):
        super(View, self).__init__(**kwargs)

    def get_kwarg(self, key, default=None):
        try:
            return self.kwargs[key]
        except KeyError:
            return default

    def validate_kwargs(self):
        '''
            If a function exists called validate_<kwargs_name>,
            it will be automatically called to validate the input
        '''
        kwargs = self.kwargs
        for k, v in kwargs.iteritems():
            func_name = 'validate_{}'.format(k)
            if func_name in dir(self):
                f = getattr(self, func_name)

                # Check f is callable
                if callable(f):
                    f(v)
                else:
                    raise validateFunctionNotCallable

    def clear_context(self):
        self.context = {}

    def add_context(self, key, value):
        if key not in self.context.keys():
            self.context[key] = value
        else:
            raise KeyError('Key alread set in context')

    def update_context(self, key, value):
        if key not in self.context.keys():
            raise KeyError('Key not set in context')
        else:
            self.context[key] = value

    def get_context(self):
        return self.context
