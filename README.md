🏏 Crickly 
================

Crickly is a simple app to store cricket match details.

📝 _Note_: Development is still in progress and not in a stable state.

Detailed documentation is in the `docs` directory. (Not produced yet. So instead heres a unicorn... 🦄)

🛫 Quick start
-------------

1. Add `crickly` to your INSTALLED_APPS setting like this

```py
    INSTALLED_APPS = [
        ...
        'crickly.core',
    ]
```

2. Include the URLconf in your project urls.py like this

```py
    path(r'^matches/', include('crickly.core.urls.matches')),
    path(r'^stats/', include('crickly.core.urls.stats')),
    path(r'^api/', include('crickly.core.urls.api')),
```

3. Run `python manage.py migrate` to create the crickly models.

4. Run `python manage.py collectstatic` to get static files.

5. Add this to your base template

```html
    <script src="{% static "crickly/scripts.js"%}"></script>
    <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
```

6. Start the development server and visit http://127.0.0.1:8000/admin/
   to create a match (you'll need the Admin app enabled).

7. Visit http://127.0.0.1:8000/matches/ to view match details.
   Visit http://127.0.0.1:8000/stats/ to view statistics.
   
   
🔧 Extensions
------------

There are several extensions to make this app more usable, they are:

- [Crickly-playcricket](https://github.com/Crickly/crickly-playcricket): This extension links the core app to the ECB Play Cricket system. It is helpful for clubs who play in leagues that require the results to be added to playcricket.
- [Crickly-matchreports](https://github.com/Crickly/crickly-matchreports): ⚙️ Under Development. This adds a match report section to the website.
- [Crickly-fantasyleague](https://github.com/Crickly/crickly-fantasyleague): ⚙️ Under Development. This adds a fantasy league section to the website. A good fundraiser for cricket clubs.
- [Crickly-PCSP-BBB](https://github.com/Crickly/crickly-pcsp-bbb): ⚙️ Under Development. This adds support for a ball by ball feed from Play Cricket Scorer Pro. Requires crickly-playcricket
