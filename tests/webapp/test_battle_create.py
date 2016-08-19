import unittest
import json
import tests.webapp.test_client


class TestBattleCreate(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_returns_201(self):
        response = self._do_attack_request(self._do_auth_request())
        self.assertEqual(201, response.status_code)

    def test_attack_and_wait_for_opponent(self):
        response = self._do_attack_request(self._do_auth_request())
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['attacker_id'])
        self.assertIsNone(response_body['defender_id'])
        self.assertEqual(1, response_body['state'])

    def test_join_battle(self):
        self._do_attack_request(self._do_auth_request())
        response = self._do_attack_request(self._do_auth_request())
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['attacker_id'])
        self.assertIsNotNone(response_body['defender_id'])
        self.assertEqual(2, response_body['state'])

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_attack_request(self, auth_token):
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': auth_token}
        )
