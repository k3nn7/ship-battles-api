import unittest
from unittest.mock import Mock
from shipbattles.service import BattleService
from shipbattles.service import AlreadyInBattleError, InvalidShipClassError
from shipbattles.service import InvalidBattleStateError, NotParticipantError
from shipbattles.service import NotAllShipsDeployedError
from shipbattles.entity import BattleState, Battle, Coordinates, Ship
from repository.memory import BattleRepository, ShipClassRepository
from shipbattles import event


class TestBattleService(unittest.TestCase):
    def setUp(self):
        self.battle_repository = BattleRepository()
        self.ship_class_repository = ShipClassRepository()
        self.event_dispatcher = Mock()
        self.battlefield_service = Mock()
        self.battle_service = BattleService(
            self.battle_repository,
            self.ship_class_repository,
            self.event_dispatcher,
            self.battlefield_service
        )

    def test_attack_and_wait_for_opponent(self):
        attacker_id = 3
        self.event_dispatcher.dispatch = Mock()
        battle = self.battle_service.attack(attacker_id)
        self.assertEqual(BattleState.looking_for_opponent, battle.state)
        self.assertEqual(attacker_id, battle.attacker_id)
        self.assertIsNone(battle.defender_id)
        assert not self.event_dispatcher.dispatch.called

    def test_start_battle_when_someone_is_looking_for_opponent(self):
        attacker_id = 3
        self.battle_repository.save(self._looking_for_opponent_battle())
        battle = self.battle_service.attack(attacker_id)
        self.assertEqual(BattleState.deploy, battle.state)
        self.assertEqual(8, battle.attacker_id)
        self.assertEqual(attacker_id, battle.defender_id)
        (self.event_dispatcher
            .dispatch
            .assert_called_with(event.Battle.deploy_finished, battle))

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

    def test_get_current_battle(self):
        account_id = 8
        battle = self.battle_service.attack(account_id)
        current_battle = self.battle_service.get_current_battle(account_id)
        self.assertEqual(battle, current_battle)

    def test_deploy_valid_ship_class(self):
        battle = self._deploy_state_battle()
        account_id = 3
        ship = Ship('is:1', Coordinates(3, 4))
        self.battle_service.deploy_ship_for_battle(
            battle.id,
            account_id,
            ship
        )
        (self.battlefield_service
            .deploy_ship_on_battlefield
            .assert_called_with(
                battle, account_id, ship))

    def test_deploy_invalid_ship_class(self):
        battle = self._deploy_state_battle()
        account_id = 3
        ship = Ship('foo', Coordinates(3, 4))
        with self.assertRaises(InvalidShipClassError):
            self.battle_service.deploy_ship_for_battle(
                battle.id, account_id, ship)

    def test_deploy_if_battle_in_invalid_state(self):
        account_id = 3
        battle = self.battle_service.attack(account_id)
        ship = Ship('is:1', Coordinates(3, 4))
        with self.assertRaises(InvalidBattleStateError):
            self.battle_service.deploy_ship_for_battle(
                battle.id, account_id, ship)

    def test_deploy_if_invalid_account_id(self):
        battle = self._deploy_state_battle()
        ship = Ship('is:1', Coordinates(3, 4))
        with self.assertRaises(NotParticipantError):
            self.battle_service.deploy_ship_for_battle(
                battle.id, 4, ship)

    def test_set_ready_state_when_not_all_ships_deployed(self):
        battle = self._deploy_state_battle()
        account_id = 3
        self.battlefield_service.mark_ready = Mock(
            side_effect=NotAllShipsDeployedError())
        with self.assertRaises(NotAllShipsDeployedError):
            self.battle_service.ready_for_battle(account_id, battle.id)

    def test_battle_keep_state_if_only_one_player_is_ready(self):
        battle = self._deploy_state_battle()
        account_id = 3
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._not_ready_for_battle_battlefield())
        self.battle_service.ready_for_battle(account_id, battle.id)
        battle = self.battle_repository.find_by_id(battle.id)
        self.assertEqual(BattleState.deploy, battle.state)

    def test_fire_exchange_when_both_players_ready(self):
        battle = self._deploy_state_battle()
        account_id = 3
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battle_service.ready_for_battle(account_id, battle.id)
        battle = self.battle_repository.find_by_id(battle.id)
        self.assertEqual(BattleState.fire_exchange, battle.state)

    def _looking_for_opponent_battle(self):
        battle = Battle()
        battle.state = BattleState.looking_for_opponent
        battle.attacker_id = 8
        return battle

    def _deploy_state_battle(self):
        attacker_id = 3
        self.battle_repository.save(self._looking_for_opponent_battle())
        return self.battle_service.attack(attacker_id)

    def _not_ready_for_battle_battlefield(self):
        battlefield = Mock()
        battlefield.ready_for_battle = False
        return battlefield

    def _ready_for_battle_battlefield(self):
        battlefield = Mock()
        battlefield.ready_for_battle = True
        return battlefield
