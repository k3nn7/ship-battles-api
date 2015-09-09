import unittest
from shipbattles.service import BattleService
from shipbattles.service import AlreadyInBattleError
from shipbattles.entity import BattleState, Battle
from repository.memory import BattleRepository


class TestBattleService(unittest.TestCase):
    def setUp(self):
        self.battle_repository = BattleRepository()
        self.battle_service = BattleService(self.battle_repository)

    def test_attack_and_wait_for_opponent(self):
        attacker_id = 3
        battle = self.battle_service.attack(attacker_id)
        self.assertEqual(BattleState.looking_for_opponent, battle.state)
        self.assertEqual(attacker_id, battle.attacker_id)
        self.assertIsNone(battle.defender_id)

    def test_start_battle_when_someone_is_looking_for_opponent(self):
        attacker_id = 3
        self.battle_repository.save(self._looking_for_opponent_battle())
        battle = self.battle_service.attack(attacker_id)
        self.assertEqual(BattleState.deploy, battle.state)
        self.assertEqual(8, battle.attacker_id)
        self.assertEqual(attacker_id, battle.defender_id)

    def test_can_not_be_in_two_battles(self):
        attacker_id = 3
        self.battle_repository.save(self._looking_for_opponent_battle())
        self.battle_service.attack(attacker_id)
        with self.assertRaises(AlreadyInBattleError):
            self.battle_service.attack(attacker_id)

    def test_can_not_look_for_another_battle_if_already_looking(self):
        attacker_id = 8
        self.battle_service.attack(attacker_id)
        with self.assertRaises(AlreadyInBattleError):
            self.battle_service.attack(attacker_id)

    def _looking_for_opponent_battle(self):
        battle = Battle()
        battle.state = BattleState.looking_for_opponent
        battle.attacker_id = 8
        return battle
