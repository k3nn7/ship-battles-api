import unittest
from shipbattles.service import BattlefieldService, NotAllShipsDeployedError
from shipbattles.entity import ShipNotInInventoryError
from shipbattles.entity import Battle, Coordinates, Ship, FireResult
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

    def test_fire_returns_fire_result(self):
        battle = self._get_battle()
        (self.battlefield_service
         .create_battlefields_for_battle(battle))
        account_id = 'id:5'
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, Ship('id:1', Coordinates(3, 4), 2))

        result = self.battlefield_service.fire(
            battle.id,
            account_id,
            Coordinates(1, 1)
        )
        self.assertEqual(FireResult.miss, result)

        result = self.battlefield_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 4)
        )
        self.assertEqual(FireResult.hit, result)

        result = self.battlefield_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 5)
        )
        self.assertEqual(FireResult.sunken, result)

    def test_fire_adds_shot_to_battlefield(self):
        battle = self._get_battle()
        (self.battlefield_service
         .create_battlefields_for_battle(battle))
        account_id = 'id:5'
        self.battlefield_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 3)
        )
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.assertEqual(1, len(battlefield.shots))
        self.assertEqual(
            Coordinates(3, 3),
            battlefield.shots[0]
        )

    def _get_battle(self):
        battle = Battle()
        battle.id = 'id:10'
        battle.attacker_id = 'id:5'
        battle.defender_id = 'id:7'
        return battle
