# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import forms
from django.contrib.auth.models import User

import json


class RegistrationForm(forms.ModelForm):
    """ Form for user registration """
    password = forms.CharField(widget=forms.PasswordInput())

    def clean_email(self):
        """ Cleans email. Checks if email is already assigned to a user """
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")  # raise error if email exists
        return email

    class Meta:
        model = User  # Model used for the form
        fields = ('first_name', 'last_name', 'email', 'password')  # fields to  be shown on form


class FantasyManageForm(forms.Form):
    """ Form to save fantasy team """
    fantasy_data = forms.CharField(
        widget=forms.HiddenInput(
            attrs={'id': 'fantasy-data-input'}  # Assigns html id for <input>
        ),  # sets field to be hidden from the user
        required=False
    )  # Defines fields on form.

    def clean_fantasy_data(self):
        """ Cleans input field. Checks if data is valid JSON """
        jdata = self.cleaned_data['fantasy_data']
        try:
            json.loads(jdata)  # Attempt to load data as JSON
        except KeyError:
            raise forms.ValidationError('Invalid data in fantasy_data')  # Raise error if not valid
        return jdata
