import unittest
from unittest.mock import Mock
from shipbattles.service import BattleService
from shipbattles.service import AlreadyInBattleError, InvalidShipClassError
from shipbattles.service import InvalidBattleStateError, NotParticipantError
from shipbattles.service import NotAllShipsDeployedError, InvalidPlayerError
from shipbattles.entity import BattleState, Coordinates, Ship
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

        self.assertEqual(
            event.Battle.deploy_finished,
            self.event_dispatcher.dispatch.call_args[0][0]
        )
        self.assertEqual(
            battle.__dict__,
            self.event_dispatcher.dispatch.call_args[0][1].__dict__
        )

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
        self.assertEqual(battle.__dict__, current_battle.__dict__)

    def test_deploy_valid_ship_class(self):
        battle = self._deploy_state_battle()
        account_id = 3
        ship = Ship('is:1', Coordinates(3, 4), 1)
        self.battle_service.deploy_ship_for_battle(
            battle.id,
            account_id,
            ship
        )

        self.assertEqual(
            battle.__dict__,
            (self.battlefield_service
             .deploy_ship_on_battlefield.call_args[0][0].__dict__)
        )
        self.assertEqual(
            account_id,
            self.battlefield_service.deploy_ship_on_battlefield.call_args[0][1]
        )
        self.assertEqual(
            ship,
            self.battlefield_service.deploy_ship_on_battlefield.call_args[0][2]
        )

    def test_deploy_invalid_ship_class(self):
        battle = self._deploy_state_battle()
        account_id = 3
        ship = Ship('foo', Coordinates(3, 4), 1)
        with self.assertRaises(InvalidShipClassError):
            self.battle_service.deploy_ship_for_battle(
                battle.id, account_id, ship)

    def test_deploy_if_battle_in_invalid_state(self):
        account_id = 3
        battle = self.battle_service.attack(account_id)
        ship = Ship('is:1', Coordinates(3, 4), 1)
        with self.assertRaises(InvalidBattleStateError):
            self.battle_service.deploy_ship_for_battle(
                battle.id, account_id, ship)

    def test_deploy_if_invalid_account_id(self):
        battle = self._deploy_state_battle()
        ship = Ship('is:1', Coordinates(3, 4), 1)
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

    def test_cannot_fire_when_not_in_fire_exchange(self):
        battle = self._deploy_state_battle()
        account_id = 3
        with self.assertRaises(InvalidBattleStateError):
            self.battle_service.fire(
                battle.id,
                account_id,
                Coordinates(3, 3)
            )
        assert not self.battlefield_service.fire.called

    def test_attacker_can_fire_in_fire_exchange(self):
        battle = self._deploy_state_battle()
        account_id = 8
        defender_id = 3
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())

        self.battle_service.ready_for_battle(account_id, battle.id)


        self.battle_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 3)
        )
        self.battlefield_service.fire.assert_called_with(
            battle.id, defender_id, Coordinates(3, 3)
        )

    def test_defender_cannot_fire_first(self):
        battle = self._deploy_state_battle()
        defender_id = 3
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battle_service.ready_for_battle(defender_id, battle.id)

        with self.assertRaises(InvalidPlayerError):
            self.battle_service.fire(
                battle.id,
                defender_id,
                Coordinates(3, 3)
            )

    def test_player_cannot_fire_twice_in_a_row(self):
        battle = self._deploy_state_battle()
        account_id = 8
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battle_service.ready_for_battle(account_id, battle.id)
        self.battle_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 3)
        )
        with self.assertRaises(InvalidPlayerError):
            self.battle_service.fire(
                battle.id,
                account_id,
                Coordinates(5, 5)
            )

    def test_players_fire_sequentialy(self):
        battle = self._deploy_state_battle()
        account_id = 8
        defender_id = 3
        self.battlefield_service.get_my_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battlefield_service.get_opponent_battlefield = Mock(
            return_value=self._ready_for_battle_battlefield())
        self.battle_service.ready_for_battle(account_id, battle.id)
        self.battle_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 3)
        )
        self.battle_service.fire(
            battle.id,
            defender_id,
            Coordinates(5, 5)
        )
        self.battle_service.fire(
            battle.id,
            account_id,
            Coordinates(3, 3)
        )

    def _looking_for_opponent_battle(self):
        return self.battle_service.attack(8)

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
