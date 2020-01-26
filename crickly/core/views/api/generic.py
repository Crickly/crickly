# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Python imports
# --None


# Django imports
from django.http import JsonResponse
from django.views.generic import View as V


# Project imports
from crickly.core.views.exceptions import validateFunctionNotCallable


class View(V):
    '''
        A Generic view used by all API views
    '''
    def __init__(self, **kwargs):
        super(View, self).__init__(**kwargs)

    def get_kwarg(self, key, default=None):
        try:
            return self.kwargs[key]
        except KeyError:
            return default

    def JsonResponse(self, data={}):
        return JsonResponse(
            {
                'error': False,
                'data': data,
            }
        )

    def error_message(self, message=""):
        return JsonResponse(
            {
                'error': True,
                'message': message,
            }
        )

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
