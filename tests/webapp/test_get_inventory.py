import unittest
import json
import tests.webapp.test_client


class TestGetInventory(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_inventory_should_be_created_for_started_battle(self):
        self._do_attack_request(self._do_auth_request())
        auth_token = self._do_auth_request()
        self._do_attack_request(auth_token)

        expected_inventory = [
            {'id': '0', 'ship_class_id': 'id:0'},
            {'id': '1', 'ship_class_id': 'id:1'}
        ]

        response = self._get_inventory_request(auth_token)
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertEqual(200, response.status_code)
        self.assertEqual(expected_inventory, response_body)

    def _do_auth_request(self):
        response = self.app.post('/api/v1/account')
        return response.headers['X-AuthToken']

    def _do_attack_request(self, auth_token):
        return self.app.post(
            '/api/v1/battle',
            headers={'X-AuthToken': auth_token}
        )

    def _get_inventory_request(self, auth_token):
        return self.app.get(
            '/api/v1/battle/my-battlefield/inventory',
            headers={'X-AuthToken': auth_token}
            )
