import unittest
import tests.webapp.test_client
import json


class TestUpdateAccount(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_204_for_valid_request_body_account_without_password(self):
        auth_token = self._do_auth_request()
        body = {
            'current_password': None,
            'new_password': 'foo'
        }
        response = self._do_update_account_request(auth_token, body)
        self.assertEqual(204, response.status_code)

    def test_401_if_invalid_auth_token(self):
        response = self._do_update_account_request('foo', {})
        self.assertEqual(401, response.status_code)

    def test_400_if_invalid_request_body(self):
        auth_token = self._do_auth_request()
        body = {
            'foo': 'bar'
        }
        response = self._do_update_account_request(auth_token, body)
        self.assertEqual(400, response.status_code)

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_update_account_request(self, auth_token, body):
        return self.app.put(
            '/api/v1/account',
            headers={
                'X-AuthToken': auth_token,
                'Content-Type': 'application/json'
            },
            data=json.dumps(body)
        )
