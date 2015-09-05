import unittest
import webapp
import json
from shipbattles import service
from repository import memory


class TestAccountRequests(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()
        webapp.app.debug = True
        webapp.app.account_service = service.AccountService(
            memory.CrudRepository()
        )

    def test_returns_201(self):
        response = self._do_request_to_account_create()
        self.assertEqual(201, response.status_code)

    def test_contains_valid_json_structure(self):
        response = self._do_request_to_account_create()
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['nick'])

    def test_contains_authentication_header(self):
        response = self._do_request_to_account_create()
        self.assertIsNotNone(response.headers['X-AuthToken'])

    def _do_request_to_account_create(self):
        return self.app.post('/api/v1/account')
