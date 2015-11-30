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

        inventory = self.ship_repository.find_by_battlefield_id(battlefield_id)
        self._assert_valid_inventory(inventory)
        self.assertTrue(self._items_have_unique_ids(inventory))

    def _assert_valid_inventory(self, inventory):
        expected_inventory = [
            {'id': 'id:2', 'ship_class_id': 'id:0'},
            {'id': 'id:3', 'ship_class_id': 'id:1'},
            {'id': 'id:0', 'ship_class_id': 'id:0'},
            {'id': 'id:1', 'ship_class_id': 'id:0'},
        ]

        self.assertEqual(4, len(inventory))
        for expected in expected_inventory:
            self.assertTrue(self._contains_ship(
                inventory=inventory,
                ship_class_id=expected['ship_class_id'],
                deployed=False
                ))

    def _contains_ship(self, inventory, ship_class_id, deployed):
        for ship in inventory:
            class_ok = ship.ship_class == ship_class_id
            if class_ok:
                return True
        return False

    def _items_have_unique_ids(self, inventory):
        ids = []
        for item in inventory:
            if item.id in ids:
                return False
            ids.append(item.id)
        return True
