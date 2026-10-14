

def payment_created(request, event, data):
    from .models import Payment
    if event == 'payment.created':
        payment_data = {key: data[key] for key in Payment.KEYS_TO_COPY}
        uuid = data.pop('uuid')
        Payment.objects.get_or_create(uuid=uuid, defaults=payment_data)
    return True

def payment_changed(request, event, data):
    from .models import Payment
    if event == 'payment.changed':
        # payment.changed can arrive before payment.created has been handled,
        # e.g. when a stored card is charged and settles right away.
        payment_data = {key: data[key] for key in Payment.KEYS_TO_COPY}
        payment, _ = Payment.objects.get_or_create(uuid=data['uuid'], defaults=payment_data)
        for attr, val in data.items():
            setattr(payment, attr, val)
        payment.save()
    return True