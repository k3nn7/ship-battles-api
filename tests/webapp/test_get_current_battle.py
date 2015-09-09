import unittest
import json
import tests.webapp.test_client


class TestGetCurrentBattle(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_return_empty_array_if_no_current_battles(self):
        auth_token = self._do_auth_request()
        response = self._do_get_curret_battle_request(auth_token)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response_body)

    def test_return_401_if_not_valid_auth_token(self):
        response = self._do_get_curret_battle_request('foo')
        self.assertEqual(401, response.status_code)

    def test_return_battle_if_in_battle(self):
        auth_token = self._do_auth_request()
        attack_response = self._do_attack_request(auth_token)
        response = self._do_get_curret_battle_request(auth_token)
        attack_response_body = json.loads(
            attack_response.get_data().decode('utf-8'))
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertEqual([attack_response_body], response_body)

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_attack_request(self, auth_token):
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': auth_token}
        )

    def _do_get_curret_battle_request(self, auth_token):
        return self.app.get(
            '/api/v1/battles',
            headers={'X-AuthToken': auth_token}
        )
