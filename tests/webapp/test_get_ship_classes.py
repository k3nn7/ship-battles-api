import unittest
import json
import tests.webapp.test_client


class TestGetShipClasses(unittest.TestCase):
    def setUp(self):
        self.app = tests.webapp.test_client.build()

    def test_returns_200(self):
        response = self._do_request()
        self.assertEqual(200, response.status_code)

    def test_contains_valid_json_structure(self):
        response = self._do_request()
        response_body = json.loads(response.get_data().decode('utf-8'))
        self.assertTrue(len(response_body) > 0)
        self.assertIsNotNone(response_body[0]['id'])
        self.assertIsNotNone(response_body[0]['name'])
        self.assertIsNotNone(response_body[0]['size'])

    def _do_request(self):
        return self.app.get('/api/v1/ship_classes')
