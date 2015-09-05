import unittest
import webapp


class TestRootRequest(unittest.TestCase):
    def setUp(self):
        self.app = webapp.app.test_client()

    def test_returns_200(self):
        response = self._do_request_to_root_url()
        self.assertEqual(200, response.status_code)

    def test_contains_valid_text(self):
        response = self._do_request_to_root_url()
        self.assertIn('ShipBattles API', response.get_data().decode('utf-8'))

    def _do_request_to_root_url(self):
        return self.app.get('/api/v1/')
