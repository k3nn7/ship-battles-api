import unittest
import json
import tests.webapp.test_client


class TestGetCurrentBattle(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_return_404_if_no_current_battles(self):
        auth_token = self._do_auth_request()
        response = self._do_get_curret_battle_request(auth_token)
        self.assertEqual(404, response.status_code)

    def test_return_401_if_not_valid_auth_token(self):
        response = self._do_get_curret_battle_request('foo')
        self.assertEqual(401, response.status_code)

    def test_return_battle_without_battlefields_if_waiting_for_opponent(self):
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        response = self._do_get_curret_battle_request(auth_token)

        response_body = json.loads(response.get_data().decode('utf-8'))

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['state'])
        self.assertIsNotNone(response_body['attacker_id'])
        self.assertIsNone(response_body['defender_id'])
        self.assertIsNone(response_body['my_battlefield'])
        self.assertIsNone(response_body['opponent_battlefield'])

    def test_return_battle_with_battlefields_when_joined_battle(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        response = self._do_get_curret_battle_request(auth_token)

        response_body = json.loads(response.get_data().decode('utf-8'))

        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertIsNotNone(response_body['state'])
        self.assertIsNotNone(response_body['attacker_id'])
        self.assertIsNotNone(response_body['defender_id'])
        self._validate_my_battlefield_in_response(response_body)

    def _validate_my_battlefield_in_response(self, response_body):
        expected_inventory = {'id:0': 1, 'id:1': 1}
        self.assertIsNotNone(response_body['my_battlefield'])
        self.assertIsNotNone(response_body['my_battlefield']['id'])
        self.assertIsNotNone(response_body['my_battlefield']['ships'])
        self.assertIsNotNone(response_body['my_battlefield']['inventory'])
        self.assertEqual(
            expected_inventory, response_body['my_battlefield']['inventory'])

    def _validate_opponent_battlefield_in_response(self, response_body):
        self.assertIsNotNone(response_body['opponent_battlefield'])
        self.assertIsNotNone(response_body['opponent_battlefield']['id'])
        self.assertNotIn('ships', response_body['opponent_battlefield'])
        self.assertNotIn('inventory', response_body['opponent_battlefield'])

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
