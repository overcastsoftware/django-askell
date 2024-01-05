# django-askell
Áskell integration for Django and Wagtail (optional)

# Installation

```shell
pip install django-askell
```

Add the app to your `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    # ... other apps
    
    'askell',

    # ... other apps
]
```

Add the app urls to your project `urls.py`:

```python
from django.urls import path, include

from askell.urls import urls as askell_urls

urlpatterns = [
    # ... your other urls
    path('askell/', include(askell_urls)),
    # ... more urls
]
```

To complete your setup, it is recommended to set up a webhook in Áskell's dashboard pointing to your website's URL. If your website has the domain `https://example.com` and you have added the app urls to your project, then the view that receives the webhooks is located at `https://example.com/askell/webhook/`.

Create your webhook, and then obtain your webhook secret and put it in your settings file or environment in your project:

```python
ASKELL_WEBHOOK_SECRET = 'my-secret'
```

# TODO

[ ] Document webhook processor
[ ] Document views
[ ] Implement subscription handling

# Release notes
## Version 0.1
* Support for creating Payment objects
* Support for webhooks processing and verification
* Default webhook processors for payment created, and changed
