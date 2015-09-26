import unittest
import json
import tests.webapp.test_client


class TestReadyForBattle(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_ready_for_battle_when_no_ships_deployed(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)

        response = self._do_ready_request(auth_token)
        self.assertEqual(400, response.status_code)

        response = self._do_get_curret_battle_request(auth_token)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(2, response_body['state'])
        self.assertFalse(response_body['my_battlefield']['ready_for_battle'])

    def test_ready_for_battle_when_all_ships_deployed(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        body = {
            'ships': [
                {'id': 'is:0', 'x': 3, 'y': 4},
                {'id': 'is:1', 'x': 5, 'y': 7}
            ]
        }
        self._deploy_request(auth_token, body)

        response = self._do_ready_request(auth_token)
        self.assertEqual(204, response.status_code)

        response = self._do_get_curret_battle_request(auth_token)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(2, response_body['state'])
        self.assertTrue(response_body['my_battlefield']['ready_for_battle'])

    def test_change_state_when_both_players_ready(self):
        body = {
            'ships': [
                {'id': 'is:0', 'x': 3, 'y': 4},
                {'id': 'is:1', 'x': 5, 'y': 7}
            ]
        }
        auth_token1 = self._do_auth_request()
        self._do_attack_request(auth_token1)

        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        self._deploy_request(auth_token, body)
        self._do_ready_request(auth_token)

        self._deploy_request(auth_token1, body)
        self._do_ready_request(auth_token1)

        response = self._do_get_curret_battle_request(auth_token)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(3, response_body['state'])

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_attack_request(self, auth_token):
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': auth_token}
        )

    def _do_ready_request(self, auth_token):
        return self.app.put(
            '/api/v1/battle/ready',
            headers={'X-AuthToken': auth_token}
        )

    def _deploy_request(self, auth_token, body):
        return self.app.put(
            '/api/v1/battle/my-battlefield',
            headers={'X-AuthToken': auth_token},
            data=json.dumps(body)
        )

    def _do_get_curret_battle_request(self, auth_token):
        return self.app.get(
            '/api/v1/battles',
            headers={'X-AuthToken': auth_token}
        )
