import unittest
import json
import tests.webapp.test_client


class TestBattleCreate(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_returns_201(self):
        response = self._do_request()
        self.assertEqual(201, response.status_code)

    def test_contains_valid_json_structure(self):
        response = self._do_request()
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['attacker_id'])

    def _do_request(self):
        response = self.app.post('/api/v1/account')
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': response.headers['X-AuthToken']}
        )
