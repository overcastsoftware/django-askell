import base64
import hashlib
import hmac
import http.client
import json
from unittest.mock import patch

from django.conf import settings
from django.test import TestCase
from django.test.client import Client
from django.contrib.auth.models import User

from askell.client import AskellClient
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

    def test_client_create_checkout_session(self):
        askell_client = AskellClient('secret-key', endpoint='https://askell.test/api')
        with patch('askell.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 201
            mock_post.return_value.json.return_value = {
                'token': 'cs_test',
                'status': 'pending',
                'sales_channel': 'memberships',
            }

            response = askell_client.create_checkout_session(
                sales_channel='memberships',
                user=self.user,
                metadata={'source': 'test'},
                theme={'primary_color': '#0F766E'},
                expires_in_seconds=3600,
            )

            self.assertEqual(response['status'], 'success')
            self.assertEqual(response['response']['token'], 'cs_test')
            mock_post.assert_called_once_with(
                'https://askell.test/api/v2/checkout-sessions/',
                headers={'Authorization': 'Api-Key secret-key'},
                json={
                    'sales_channel': 'memberships',
                    'customer_reference': str(self.user.pk),
                    'metadata': {'source': 'test'},
                    'theme': {'primary_color': '#0F766E'},
                    'expires_in_seconds': 3600,
                },
            )

    def test_client_create_checkout_session_error_includes_response(self):
        askell_client = AskellClient('secret-key', endpoint='https://askell.test/api')
        with patch('askell.client.requests.post') as mock_post:
            mock_post.return_value.status_code = 400
            mock_post.return_value.json.return_value = {
                'sales_channel': ['Sales channel not found for account.'],
            }

            response = askell_client.create_checkout_session(
                sales_channel='missing',
                customer_reference='customer-1',
            )

            self.assertEqual(response['status'], 'error')
            self.assertEqual(response['status_code'], 400)
            self.assertEqual(
                response['response']['sales_channel'],
                ['Sales channel not found for account.'],
            )

    def test_checkout_session_view_creates_session_for_logged_in_user(self):
        with patch('askell.views.client.create_checkout_session') as mock_create:
            mock_create.return_value = {
                'status': 'success',
                'status_code': 201,
                'response': {
                    'token': 'cs_test',
                    'status': 'pending',
                    'sales_channel': 'memberships',
                },
            }

            response = self.client.post(
                '/askell/checkout-session/',
                data={
                    'sales_channel': 'memberships',
                    'metadata': {'source': 'test'},
                    'theme': {'primary_color': '#0F766E'},
                    'expires_in_seconds': 3600,
                },
                content_type='application/json',
            )

            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json()['response']['token'], 'cs_test')
            mock_create.assert_called_once_with(
                sales_channel='memberships',
                user=self.user,
                metadata={'source': 'test'},
                theme={'primary_color': '#0F766E'},
                expires_in_seconds=3600,
            )

    def test_checkout_session_view_requires_sales_channel(self):
        response = self.client.post(
            '/askell/checkout-session/',
            data={},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['status'], 'error')

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

    def post_webhook(self, event, data):
        body = json.dumps({'event': event, 'ref': None, 'sender': 'tumi@overcast.is', 'data': data}).encode()
        digest = hmac.new(settings.ASKELL_WEBHOOK_SECRET.encode(), body, hashlib.sha512).digest()
        headers = {
            'Hook-Hmac': base64.b64encode(digest).decode(),
            'Hook-Event': event,
        }
        return self.client.post('/askell/webhook/', data=body, headers=headers, content_type='application/json')

    def test_webhook_payment_changed_before_payment_created(self):
        # A payment charged straight away can settle before its payment.created
        # webhook has been handled, so payment.changed may arrive first.
        data = {
            "uuid": "5f0c1e2a-7d4b-4c55-9a51-3f0f5b0c2d11",
            "amount": "2000.0000",
            "currency": "ISK",
            "description": "wesd",
            "reference": "q324erdf2",
            "state": "settled",
            "created_at": "2024-02-16T12:52:36.334898Z",
            "updated_at": "2024-02-16T12:52:37.450551Z",
            "transactions": [],
        }
        response = self.post_webhook('payment.changed', data)
        self.assertEqual(response.status_code, 200)

        payment = Payment.objects.get(uuid=data['uuid'])
        self.assertEqual(payment.state, 'settled')
        self.assertEqual(payment.reference, 'q324erdf2')

        # The late payment.created must not reset the payment to pending.
        response = self.post_webhook('payment.created', dict(data, state='pending'))
        self.assertEqual(response.status_code, 200)

        payment.refresh_from_db()
        self.assertEqual(payment.state, 'settled')
