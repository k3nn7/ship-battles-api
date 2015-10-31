import unittest
import json
import tests.webapp.test_client


class TestDeployShip(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_deploy_single_ship(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        body = {
            'ships': [
                {'id': 'id:1', 'x': 3, 'y': 4}
            ]
        }
        expected_inventory = {'id:1': 0, 'id:0': 1}
        response = self._deploy_request(auth_token, body)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(body['ships'], response_body['ships'])
        self.assertEqual(expected_inventory, response_body['inventory'])

    def test_deploy_multiple_ships(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        body = {
            'ships': [
                {'id': 'id:0', 'x': 3, 'y': 4},
                {'id': 'id:1', 'x': 5, 'y': 7}
            ]
        }
        expected_inventory = {'id:0': 0, 'id:1': 0}
        response = self._deploy_request(auth_token, body)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(body['ships'], response_body['ships'])
        self.assertEqual(expected_inventory, response_body['inventory'])

    def test_deploy_invalid_ship_class(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        body = {
            'ships': [
                {'id': 'id:3', 'x': 3, 'y': 4}
            ]
        }
        expected_inventory = {'id:1': 1, 'id:0': 1}
        response = self._deploy_request(auth_token, body)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertEqual([], response_body['ships'])
        self.assertEqual(expected_inventory, response_body['inventory'])

    def test_deploy_multiple_ships_some_invalid(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)
        body = {
            'ships': [
                {'id': 'id:0', 'x': 3, 'y': 4},
                {'id': 'id:1', 'x': 5, 'y': 7},
                {'id': 'id:2', 'x': 5, 'y': 7},
                {'id': 'id:3', 'x': 5, 'y': 7},
            ]
        }
        expected_inventory = {'id:0': 0, 'id:1': 0}
        response = self._deploy_request(auth_token, body)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_body['id'])
        self.assertEqual(body['ships'][:2], response_body['ships'])
        self.assertEqual(expected_inventory, response_body['inventory'])

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_attack_request(self, auth_token):
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': auth_token}
        )

    def _deploy_request(self, auth_token, body):
        return self.app.put(
            '/api/v1/battle/my-battlefield',
            headers={'X-AuthToken': auth_token},
            data=json.dumps(body)
        )
