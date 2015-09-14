import unittest
from shipbattles.service import BattlefieldService
from shipbattles.entity import Battle
from repository.memory import CrudRepository


class TestBattlefieldService(unittest.TestCase):
    def setUp(self):
        self.battlefield_repository = CrudRepository()
        self.battlefield_service = BattlefieldService(
            self.battlefield_repository
        )

    def test_create_battlefields_for_battle(self):
        battle = Battle()
        battle.id = 'id:10'
        battle.attacker_id = 'id:5'
        battle.defender_id = 'id:7'
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
