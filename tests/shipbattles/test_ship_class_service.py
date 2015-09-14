import unittest
from shipbattles.service import ShipClassService
from shipbattles.entity import ShipClass
from repository.memory import ShipClassRepository


class TestShipClassService(unittest.TestCase):
    def setUp(self):
        self.ship_class_repository = ShipClassRepository()
        self.ship_class_service = ShipClassService(self.ship_class_repository)

    def test_return_list_of_available_ship_classes(self):
        ship_classes = self.ship_class_service.get_all()
        self.assertTrue(len(ship_classes) > 0)
        for ship_class in ship_classes:
            self.assertIsInstance(ship_class, ShipClass)
