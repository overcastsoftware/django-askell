import http.client
from unittest.mock import patch

from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from askell.models import Payment

http.client.HTTPConnection.debuglevel = 1

class BaseTestCase(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='user', email='user@example.com')
        self.client = Client()
        self.client.force_login(self.user)

        self.existing_payment = Payment.objects.create(
            uuid="830a1b4a-113f-41f5-8112-d82e2b0b3956",
            amount="1.0000",
            currency="ISK",
            description="wesd",
            reference="q324erdf",
            user=self.user,
        )

class TestViews(BaseTestCase):

    def test_create_payment(self):
        payment_count_before = Payment.objects.count()
        with patch('askell.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                "uuid": "830a1b4a-113f-41f5-8112-d82e2b0b3957",
                "amount": "1.0000",
                "currency": "ISK",
                "description": "wesd",
                "reference": "q324erdf1",
                "state": "pending",
                "created_at": "2024-01-05T11:21:49.425825Z",
                "updated_at": "2024-01-05T11:21:49.425847Z",
                "transactions": []
            }

            response = self.client.post('/askell/payment/')
            self.assertEqual(response.status_code, 201)

            payment_count_after = Payment.objects.count()

            self.assertNotEqual(payment_count_before, payment_count_after)

    def test_get_payment(self):
        response = self.client.get('/askell/payment/830a1b4a-113f-41f5-8112-d82e2b0b3956/')
        self.assertEqual(response.status_code, 200)

    def test_webhook_payment_created(self):
        payment_count_before = Payment.objects.count()
        payload = '{"event": "payment.created", "ref": null, "sender": "tumi@overcast.is", "data": {"uuid": "830a1b4a-113f-41f5-8112-d82e2b0b3956", "amount": "1.0000", "currency": "ISK", "description": "wesd", "reference": "q324erdf", "state": "pending", "created_at": "2024-01-05T11:21:49.425825Z", "updated_at": "2024-01-05T11:21:49.425847Z", "transactions": []}}'
        headers = {
            'HOOK_SUBSCRIPTION': 'b03230d7-1005-44fc-b297-b3d2abf0fcd6',
            'HOOK_HMAC': 'z9sFmAUAvZeA7PKNX6RBxhJbdpwReLMJeMell7LJwtkxX9cQoSWTE/W622EM8BoPfcS/42sDii2/QqNYg5lHiw==',
            'HOOK_EVENT': 'payment.created',
            'HOOK_DELIVERY': 'dc3511de-0af7-4f3c-84a8-06a3e60439c5',
        }
        self.client.post('/askell/webhook/', data=payload, headers=headers, content_type='application/json')
        payment_count_after = Payment.objects.count()
        self.assertEqual(payment_count_before, payment_count_after)


    def test_webhook_payment_settled(self):
        payment_count_before = Payment.objects.count()
        payment = Payment.objects.get(uuid="830a1b4a-113f-41f5-8112-d82e2b0b3956")
        self.assertFalse(payment.state == "settled")
        payload = '{"event": "payment.changed", "ref": null, "sender": "tumi@overcast.is", "data": {"uuid": "830a1b4a-113f-41f5-8112-d82e2b0b3956", "amount": "1.0000", "currency": "ISK", "description": "wesd", "reference": "q324erdf", "state": "settled", "created_at": "2024-01-05T11:21:49.425825Z", "updated_at": "2024-01-05T11:21:53.664259Z", "transactions": [{"external_reference": "400511385256", "data": {"id": "400511385256", "receipt": {"acquirerReferenceNumber": "385256", "authenticationMethod": "NONE", "authorizationCode": "593443", "authorizationResponseTime": "00:00:00", "authorizedAmount": 100, "cardInformation": {"cardCategory": "Corporate", "cardProductCategory": "MCP", "cardScheme": "M", "cardUsage": "Credit", "issuingCountry": "IS", "outOfScaScope": false}, "correlationID": "71ca5168-100e-4c05-9b08-d50512c1ea6e", "currency": "352", "isCardPresent": false, "isSuccess": true, "marketInformation": {"acquirerRegion": "Rapyd Europe EEA", "marketName": "Domestic", "merchantCountry": "IS"}, "maskedCardNumber": "555016******1024", "responseCode": "00-I", "responseDescription": "Approved or completed successfully.", "responseTime": "00:00:03", "transactionID": "400511385256", "transactionLifecycleId": "ABC2220020105", "transactionType": "12"}, "status": "settled"}, "state": "settled", "uuid": "e858bc16-3a62-41a7-a087-367ed02dc63e", "fail_code": null, "refund_code": null, "cancel_code": null, "amount": "1.00", "currency": "ISK", "payment_method": {"verified": true, "canceled": false, "valid_until": "2026-10-01T00:00:00Z", "display_info": "XXXX-XXXX-XXXX-1024 (MasterCard)", "credit_card": true}, "created_at": "2024-01-05T11:21:49.455071Z"}]}}'
        headers = {
            'Hook-Subscription': 'b03230d7-1005-44fc-b297-b3d2abf0fcd6',
            'Hook-Hmac': '0fjBVLt7GJ/7jkFSyK3RmGxYz1Jna11XCI1qNJUiHI4V2zKqpaIlyAYbHoXBA65GE9Rp9h/UjMHTHy2UXbo8wg==',
            'Hook-Event': 'payment.changed',
            'Hook-Delivery': '6b5583cc-727c-4d01-950d-7b8a2f683d09',
        }
        self.client.post('/askell/webhook/', data=payload, headers=headers, content_type='application/json')
        payment_count_after = Payment.objects.count()
        self.assertEqual(payment_count_before, payment_count_after)
        payment.refresh_from_db()
        self.assertTrue(payment.state == "settled")