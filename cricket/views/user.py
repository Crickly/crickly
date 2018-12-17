# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# Django imports
from django.shortcuts import render, render_to_response
from django.contrib.auth.models import User
from django.contrib.auth.views import login as default_login_view
from django.template import RequestContext
from django.core.mail import send_mail
from django.conf import settings


# Python imports
from passlib.hash import pbkdf2_sha256
from uuid import uuid4


# Project imports
from cricket.models import ActivationCode
from cricket.forms import RegistrationForm
from tools.decorators import anonymous_required


# Account register view
@anonymous_required
def register(request):
    context = RequestContext(request)
    registered = False
    # Check if form was submitted or is new page load
    if request.method == 'POST':
        # Form submitted
        # Load registration form with previous data
        user_form = RegistrationForm(data=request.POST)
        if user_form.is_valid():  # Check if form is valid
            user = user_form.save()  # Save user data to the database.
            user.set_password(user.password)  # Add users password
            user.username = user.email  # Set username to email
            user.is_active = False
            user.save()  # Save user

            # Create activation code
            un_hashed = uuid4().__str__()
            activation_code = ActivationCode(
                activation_code=pbkdf2_sha256.encrypt(
                    un_hashed,
                    rounds=200000,
                    salt_size=16
                )
            )
            activation_code.user_id = user.id
            activation_code.save()  # Save activation code to database
            # Send activation email
            send_mail(
                'Activate your KVCC account',
                '''Please use the following link to activate your account
for Knowle Village Cricket Club
https://www.knowlevillagecc.co.uk/user/activate/{0}/{1}/'''.format(user.id, un_hashed),
                settings.SERVER_EMAIL,
                [user.email],
                fail_silently=False,
            )
            registered = True
    else:
        # New page load create blank form
        user_form = RegistrationForm()
    # Render page with current form data
    return render_to_response(
        'registration/register.html',
        {'user_form': user_form, 'registered': registered},
        context,
    )


# Account activation view
@anonymous_required
def activate(request, user_id, user_activation_code):
    # Fetch activation code for the user
    activation_codes = ActivationCode.objects.filter(user__id=user_id)
    if activation_codes is not None:  # Check there is an activation code in database for user
        try:
            if pbkdf2_sha256.verify(
                user_activation_code,
                activation_codes[0].activation_code
            ):  # Verify activation code
                # Valid activation code. Activate account
                user = User.objects.filter(id=user_id)[0]
                user.is_active = True
                user.save()
                activation_codes.delete()  # Remove activation code
                success = True
            else:
                success = False
        except IndexError:
            success = False
    else:
        success = False
    # Render page
    return render(
        request,
        'registration/activate.html',
        context={'success': success}
    )


# Login view
@anonymous_required
def custom_login(request):
    return default_login_view(request)
