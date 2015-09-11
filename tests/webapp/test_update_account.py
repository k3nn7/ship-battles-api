import unittest
import tests.webapp.test_client
import json


class TestUpdateAccount(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_204_for_valid_update_password_request_without_password(self):
        auth_token = self._do_auth_request()
        body = {
            'current_password': None,
            'new_password': 'foo'
        }
        response = self._do_update_password_request(auth_token, body)
        self.assertEqual(204, response.status_code)

    def test_401_update_password_if_invalid_auth_token(self):
        response = self._do_update_password_request('foo', {})
        self.assertEqual(401, response.status_code)

    def test_400_update_password_if_invalid_request_body(self):
        auth_token = self._do_auth_request()
        body = {
            'foo': 'bar'
        }
        response = self._do_update_password_request(auth_token, body)
        self.assertEqual(400, response.status_code)

    def test_400_update_password_if_invalid_password(self):
        auth_token = self._do_auth_request()
        body = {
            'current_password': None,
            'new_password': ''
        }
        response = self._do_update_password_request(auth_token, body)
        self.assertEqual(400, response.status_code)

    def test_204_update_nickname(self):
        auth_token = self._do_auth_request()
        body = {
            'nickname': 'foobar',
        }
        response = self._do_update_nickname_request(auth_token, body)
        self.assertEqual(204, response.status_code)

    def test_401_update_nickname_invalid_token(self):
        body = {
            'nickname': 'foobar',
        }
        response = self._do_update_nickname_request('foo', body)
        self.assertEqual(401, response.status_code)

    def test_400_update_nickname_invalid_nickname(self):
        auth_token = self._do_auth_request()
        body = {
            'nickname': '',
        }
        response = self._do_update_nickname_request(auth_token, body)
        self.assertEqual(400, response.status_code)

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_update_password_request(self, auth_token, body):
        return self.app.put(
            '/api/v1/account/password',
            headers={
                'X-AuthToken': auth_token,
                'Content-Type': 'application/json'
            },
            data=json.dumps(body)
        )

    def _do_update_nickname_request(self, auth_token, body):
        return self.app.put(
            '/api/v1/account/nickname',
            headers={
                'X-AuthToken': auth_token,
                'Content-Type': 'application/json'
            },
            data=json.dumps(body)
        )
