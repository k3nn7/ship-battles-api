import unittest
from shipbattles.service import BattlefieldService, NotAllShipsDeployedError
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
            battle, account_id,
            Ship('id:2', Coordinates(3, 4), 2, Orientation.vertical))

        with self.assertRaises(NotAllShipsDeployedError):
            self.battlefield_service.mark_ready(battlefields[0].id)

    def test_mark_battlefield_ready_when_all_ships_deployed(self):
        battle = self._get_battle()
        battlefields = (self.battlefield_service
                        .create_battlefields_for_battle(battle))
        account_id = 'id:5'
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id,
            Ship('id:1', Coordinates(3, 4), 1, Orientation.horizontal))
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id,
            Ship('id:2', Coordinates(3, 4), 2, Orientation.vertical))

        self.battlefield_service.mark_ready(battlefields[0].id)
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.assertTrue(battlefield.ready_for_battle)

    def _get_battle(self):
        battle = Battle()
        battle.id = 'id:10'
        battle.attacker_id = 'id:5'
        battle.defender_id = 'id:7'
        return battle
