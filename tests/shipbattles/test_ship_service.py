import unittest
from shipbattles.service import ShipService
from repository.memory import ShipRepository, ShipClassRepository
from repository import serializer


class TestShipService(unittest.TestCase):
    def setUp(self):
        self.ship_repository = ShipRepository(
            serializer.ShipSerializer())
        self.ship_class_repository = ShipClassRepository(
            serializer.ShipClassSerializer())
        self.ship_service = ShipService(
            self.ship_repository, self.ship_class_repository)

    def test_create_inventory(self):
        battlefield_id = "id:99"
        inventory_configuration = {'id:0': 3, 'id:1': 1}

        self.ship_service.create_inventory(
            battlefield_id, inventory_configuration)

        expected_inventory = [
            {'id': 'id:2', 'ship_class_id': 'id:0'},
            {'id': 'id:3', 'ship_class_id': 'id:1'},
            {'id': 'id:0', 'ship_class_id': 'id:0'},
            {'id': 'id:1', 'ship_class_id': 'id:0'},
        ]

        inventory = self.ship_repository.find_by_battlefield_id(battlefield_id)
        self.assertEqual(4, len(inventory))

        for expected in expected_inventory:
            self.assertTrue(self._assert_contains_ship(expected, inventory))

    def _assert_contains_ship(self, ship_params, inventory):
        for ship in inventory:
            id_ok = ship.id == ship_params['id']
            class_ok = ship.ship_class == ship_params['ship_class_id']
            if id_ok and class_ok:
                return True
        return False
