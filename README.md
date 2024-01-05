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

Obtain your webhook secret from askell.is and put it in your settings file or environment:

```python
ASKELL_WEBHOOK_SECRET = 'my-secret'
```