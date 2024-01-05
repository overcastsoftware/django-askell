import requests
from django.http import HttpResponseBadRequest

# from .models import Plan, Subscription
from .settings import ASKELL_ENDPOINT, ASKELL_SECRET_KEY
from .utils import get_customer_reference_from_user


class AskellClient:

    def __init__(self, token, endpoint=None):
        self.TOKEN = token
        if endpoint:
            self.ENDPOINT = endpoint

    def _build_url(self, path):
        return "{}{}".format(self.ENDPOINT, path)

    @property
    def _auth(self):
        return {
            "Authorization": "Api-Key {}".format(self.TOKEN)
        }

    def get_subscriptions(self, id=None):
        path = '/subscriptions/'
        if id: 
            path = "/subscriptions/{}/".format(id)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()

    def get_plans(self, id=None):
        path = '/plans/'
        if id: 
            path = "/plans/{}/".format(id)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()
    
    def make_payment(self, user, amount, currency, reference, description=None):
        customer_reference = get_customer_reference_from_user(user)
        path = '/payments/'
        data = {
            "customer_reference": customer_reference,
            "amount": amount,
            "currency": currency,
            "reference": reference,
        }
        if description:
            data["description"] = description
        response = requests.post(self._build_url(path), headers=self._auth, data=data)
        return response.json()
    
    def get_payment(self, uuid):
        path = '/payments/{}/'.format(uuid)
        response = requests.get(self._build_url(path), headers=self._auth)
        return response.json()

    # def subscribe(self, user=None, plan=None):
    #     if user and plan:
    #         subscription = Subscription.objects.get_or_create(user=user)
    #         subscription.plan = plan
    #         subscription.save()  


client = AskellClient(ASKELL_SECRET_KEY, endpoint=ASKELL_ENDPOINT)
