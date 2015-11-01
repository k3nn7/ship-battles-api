import unittest
from shipbattles.service import BattlefieldService
from shipbattles.entity import ShipNotInInventoryError
from shipbattles.entity import Battle, Coordinates, Ship, Orientation
from repository.memory import BattlefieldRepository
from repository import serializer


class TestBattlefieldService(unittest.TestCase):
    def setUp(self):
        battlefield_inventory = {
            'id:1': 1,
            'id:2': 1
        }
        self.battlefield_repository = BattlefieldRepository(
            serializer.BattlefieldSerializer())
        self.battlefield_service = BattlefieldService(
            self.battlefield_repository,
            battlefield_inventory
        )

    def test_deploy_ship_on_battlefield(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:1', Coordinates(3, 4), 3, Orientation.vertical)

        returned = self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, ship)
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.assertEqual(battlefield.id, returned.id)

        self.assertTrue(len(battlefield.ships) == 1)
        self.assertEqual(ship.coordinates, battlefield.ships[0].coordinates)
        self.assertEqual(ship.ship_class, battlefield.ships[0].ship_class)
        self.assertEqual(ship.orientation, battlefield.ships[0].orientation)

    def test_deploy_ship_that_is_not_in_inventory(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:10', Coordinates(3, 4), 2, Orientation.horizontal)
        with self.assertRaises(ShipNotInInventoryError):
            self.battlefield_service.deploy_ship_on_battlefield(
                battle, account_id, ship)

    def test_deploy_ship_that_no_more_in_inventory(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:1', Coordinates(3, 4), 1, Orientation.horizontal)
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, ship)
        with self.assertRaises(ShipNotInInventoryError):
            self.battlefield_service.deploy_ship_on_battlefield(
                battle, account_id, ship)

    def _get_battle(self):
        battle = Battle()
        battle.id = 'id:10'
        battle.attacker_id = 'id:5'
        battle.defender_id = 'id:7'
        return battle
