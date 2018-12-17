# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from cricket.views import user

# Define URL patterns
urlpatterns = [
    # url(regex, view, name)
    url(r'^register/$', user.register, name='register'),
    url(r'^login/$', user.custom_login, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
    url(
        r'^activate/(?P<user_id>[0-9]*)/(?P<user_activation_code>[\w-]+)/$',
        user.activate,
        name='activate'
    ),
]
