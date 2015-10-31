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

    def test_create_battlefields_for_battle(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))
        self.assertTrue(len(battlefields) == 2)
        self.assertEqual(battle.id, battlefields[0].battle_id)
        self.assertEqual(battle.id, battlefields[1].battle_id)
        self.assertEqual(battle.attacker_id, battlefields[0].account_id)
        self.assertEqual(battle.defender_id, battlefields[1].account_id)

        self.assertIsNotNone(
            self.battlefield_repository.find_by_id(battlefields[0].id)
        )
        self.assertIsNotNone(
            self.battlefield_repository.find_by_id(battlefields[1].id)
        )
        self.assertTrue(len(battlefields[0].ships) == 0)
        self.assertTrue(len(battlefields[1].ships) == 0)

    def test_get_my_battlefield_for_battle(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))

        my_battlefield = self.battlefield_service.get_my_battlefield(
            battle,
            battle.attacker_id
        )

        self.assertEqual(battlefields[0].id, my_battlefield.id)
        self.assertEqual(battle.id, my_battlefield.battle_id)
        self.assertEqual(battle.attacker_id, my_battlefield.account_id)

    def test_get_opponent_battlefield_for_battle(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))

        my_battlefield = self.battlefield_service.get_opponent_battlefield(
            battle,
            battle.attacker_id
        )

        self.assertEqual(battlefields[1].id, my_battlefield.id)
        self.assertEqual(battle.id, my_battlefield.battle_id)
        self.assertEqual(battle.defender_id, my_battlefield.account_id)

    def test_deploy_ship_on_battlefield(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:1', Coordinates(3, 4), 1)

        returned = self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, ship)
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.assertEqual(battlefield.id, returned.id)

        self.assertTrue(len(battlefield.ships) == 1)
        self.assertEqual(ship.coordinates, battlefield.ships[0].coordinates)
        self.assertEqual(ship.ship_class, battlefield.ships[0].ship_class)

    def test_deploy_ship_that_is_not_in_inventory(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:10', Coordinates(3, 4), 2)
        with self.assertRaises(ShipNotInInventoryError):
            self.battlefield_service.deploy_ship_on_battlefield(
                battle, account_id, ship)

    def test_deploy_ship_that_no_more_in_inventory(self):
        battle = self._get_battle()
        self.battlefield_service.create_battlefields_for_battle(battle)

        account_id = 'id:5'
        ship = Ship('id:1', Coordinates(3, 4), 1)
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, ship)
        with self.assertRaises(ShipNotInInventoryError):
            self.battlefield_service.deploy_ship_on_battlefield(
                battle, account_id, ship)

    def test_mark_battlefield_ready_when_no_ships_deployed(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))
        with self.assertRaises(NotAllShipsDeployedError):
            self.battlefield_service.mark_ready(battlefields[0].id)

    def test_mark_battlefield_ready_when_not_all_ships_deployed(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))
        account_id = 'id:5'
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, Ship('id:2', Coordinates(3, 4), 2))

        with self.assertRaises(NotAllShipsDeployedError):
            self.battlefield_service.mark_ready(battlefields[0].id)

    def test_mark_battlefield_ready_when_all_ships_deployed(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))
        account_id = 'id:5'
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, Ship('id:1', Coordinates(3, 4), 1))
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, Ship('id:2', Coordinates(3, 4), 2))

        self.battlefield_service.mark_ready(battlefields[0].id)
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.assertTrue(battlefield.ready_for_battle)

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
