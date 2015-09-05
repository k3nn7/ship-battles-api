import unittest
import webapp
import json


class TestAccountRequests(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()

    def test_returns_201(self):
        response = self._do_request_to_root_url()
        self.assertEqual(201, response.status_code)

    def test_contains_valid_json_structure(self):
        response = self._do_request_to_root_url()
        expected_body = {'id': 'foo123', 'nick': 'testuser'}
        self.assertEqual(
            expected_body,
            json.loads(response.get_data().decode('utf-8'))
        )

    def test_contains_authentication_header(self):
        response = self._do_request_to_root_url()
        self.assertIn('X-AuthToken', response.headers)
        self.assertEqual('foobar', response.headers['X-AuthToken'])

    def _do_request_to_root_url(self):
        return self.app.post('/api/v1/account')
