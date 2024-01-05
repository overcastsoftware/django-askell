WEBHOOK_HANDLERS = []

def get_webhook_handlers():
    return WEBHOOK_HANDLERS


def register_webhook_handler(func):
    if func not in WEBHOOK_HANDLERS:
        WEBHOOK_HANDLERS.append(func)
    return func


def run_webhook_handlers(request, event, data):
    for func in WEBHOOK_HANDLERS:
        if not func(request, event, data):
            return False
    return True