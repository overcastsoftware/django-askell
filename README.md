# django-askell
Áskell integration for Django and Wagtail (optional)

<a href="https://github.com/overcastsoftware/django-askell/actions">
    <img src="https://github.com/overcastsoftware/django-askell/workflows/django-askell%20CI/badge.svg" alt="Build Status" />
</a>


## Installation

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

Then go to Áskell, create a public/private key pair and add these keys to your settings file or environment in your project:
```python
ASKELL_PUBLIC_KEY = 'my-public-key'
ASKELL_SECRET_KEY = 'my-secret-key'
```

To complete your setup, it is recommended to set up a webhook in Áskell's dashboard pointing to your website's URL. If your website has the domain `https://example.com` and you have added the app urls to your project, then the view that receives the webhooks is located at `https://example.com/askell/webhook/`.

Create your webhook, and then obtain your webhook secret and put it in your settings file or environment in your project:

```python
ASKELL_WEBHOOK_SECRET = 'my-secret'
```

## Webhook handlers

You can register new webhook handlers if you want to implement custom logic when something happens in Áskell.
These are the default webhook handlers:

```
askell.webhook_handlers.payment_created
askell.webhook_handlers.payment_changed
```

Registering a new handler is simple:

```python
from askell.webhooks import register_webhook_handler

@register_webhook_handler
def payment_settled(request, event, data):
    from .models import Payment
    if event == 'payment.changed':
        if data['state'] == 'settled':
            # do something here
    return True
```

## V2 checkout sessions

For product/contract based subscriptions, create a scoped checkout session on your Django server and pass the returned browser-safe token to `askell.js`. Do not expose `ASKELL_SECRET_KEY` in the browser.

```python
from askell.client import client


def create_membership_checkout(request):
    result = client.create_checkout_session(
        sales_channel='memberships',
        user=request.user,
        metadata={'source': 'membership-page'},
        expires_in_seconds=3600,
    )
    if result['status'] != 'success':
        # handle result['response'] or result['message']
        ...
    return JsonResponse({'sessionToken': result['response']['token']})
```

The package also includes a logged-in helper endpoint at `/askell/checkout-session/`. You can post a sales channel reference to it, or subclass `CheckoutSessionView` and set `sales_channel` to keep the channel fixed server-side.

```python
from askell.views import CheckoutSessionView


class MembershipCheckoutSessionView(CheckoutSessionView):
    sales_channel = 'memberships'
```

Mount the widget with the token returned by your Django backend:

```html
<script src="https://js.askell.is/v2/askell.js"></script>
<div id="askell-checkout"></div>
<script>
  fetch("/membership/checkout-session/", { method: "POST" })
    .then((response) => response.json())
    .then(({ sessionToken }) => {
      Askell.mountCheckout("#askell-checkout", {
        sessionToken: sessionToken,
        onSuccess: function (result) {
          console.log(result.contractId);
        }
      });
    });
</script>
```

## Releasing

Bump the version in `setup.py` and `release.sh`, add release notes below and commit. Then run:

```bash
./docker-release.sh
```

This builds the package and uploads it to PyPI from a `python:3.12-slim` container, so it doesn't depend on your local Python. It reads PyPI credentials from `~/.pypirc` or the `TWINE_USERNAME` and `TWINE_PASSWORD` environment variables, and refuses to run with uncommitted changes.

## TODO

- [x] Document webhook handlers
- [ ] Document views
- [x] Add V2 checkout session helper
- [ ] Document product/contract entitlement helpers

## Release notes

### Version 0.1.26
* The default `payment_changed` webhook handler creates the payment if `payment.created` hasn't been handled yet, instead of raising `Payment.DoesNotExist`
* Add `docker-release.sh` for building and uploading releases from a Docker container

### Version 0.1.25
* Add V2 checkout session client helper and Django view for scoped checkout sessions
* Add README documentation for creating browser-safe checkout sessions for `askell.js`
* Add release extra dependencies and safer PyPI release scripts

### Version 0.1.24
* Checkout support updated

### Version 0.1.23
* Set default auto field to BigAutoField to prevent projects creating migrations for django-askell

### Version 0.1.22
* Support for refunding single payments

### Version 0.1.21
* Fixing a bug in the settings module 

### Version 0.1.20
* Adding a setting to disable default webhook handlers. Also a new function to unregister webhook handlers.

### Version 0.1.19
* Adding payment method import method

### Version 0.1.7
* Fixed a bug in creating a customer

### Version 0.1.6
* Added support for multiple states

### Version 0.1.5
* Fixed a bug with imports

### Version 0.1.4
* Fixed a bug in the Payment detail view

### Version 0.1.3
* Fixed a bug in webhook handler

### Version 0.1.2
* Added logging mechanism for debugging

### Version 0.1.1
* Changed the way webhook handlers are imported and documented

### Version 0.1
* Support for creating Payment objects
* Support for webhooks processing and verification
* Default webhook handlers for payment created, and changed
