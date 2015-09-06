import unittest
import json
import tests.webapp.test_client


class TestGetAuthenticatedAccount(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_return_401_if_not_authenticated(self):
        response = self.app.get('/api/v1/account')
        self.assertEqual(401, response.status_code)

    def test_return_200_if_authorized(self):
        response = self._do_request()
        self.assertEqual(200, response.status_code)

    def test_returns_valid_json_structure(self):
        response = self._do_request()
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['nick'])

    def _do_request(self):
        response = self.app.post('/api/v1/account')
        return self.app.get(
            '/api/v1/account',
            headers={'X-AuthToken': response.headers['X-AuthToken']}
        )
