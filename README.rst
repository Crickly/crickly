================
django-cricket 🏏
================

Django-Cricket is a simple app to store cricket match details.

📝 **Note**: Development is still in progress and not in a stable state. I doubt it'll work yet! 🤪

Detailed documentation is in the "docs" directory. (Not produced yet...)

-------------
Quick start 😇
-------------

1. Add "cricket" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'cricket',
    ]

2. Include the polls URLconf in your project urls.py like this::

    path('cricket/', include('cricket.urls')),

3. Run `python manage.py migrate` to create the polls models.

4. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a match (you'll need the Admin app enabled).

5. Visit http://127.0.0.1:8000/cricket/ to view match details.
