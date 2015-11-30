from shipbattles.entity import Account, SessionToken, Battle, BattleState
from shipbattles.entity import Battlefield, FireResult, Ship, Coordinates
from shipbattles.entity import InvalidPasswordError, InvalidNicknameError
from shipbattles.entity import Orientation
from shipbattles import event
import time
from copy import copy


class AccountService:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def create_random_account(self):
        nick = 'user%s' % int(time.time())
        account = Account(nick)
        return self.account_repository.save(account)

    def update_password(self, account_id, previous_password, new_password):
        account = self.account_repository.find_by_id(account_id)
        self._validate_previous_password(account, previous_password)
        try:
            account.set_password(new_password)
        except InvalidPasswordError:
            raise ValidationError({'password': 'invalid'})
        self.account_repository.save(account)

    def update_nickname(self, account_id, nickname):
        if not self._is_nickname_available(nickname):
            raise ValidationError({'nickname': 'invalid'})
        account = self.account_repository.find_by_id(account_id)
        try:
            account.set_nickname(nickname)
        except InvalidNicknameError:
            raise ValidationError({'nickname': 'invalid'})
        self.account_repository.save(account)

    def _validate_previous_password(self, account, previous_password):
        if account.is_secured():
            if not account.password_valid(previous_password):
                raise ValidationError({'previous_password': 'invalid'})

    def _is_nickname_available(self, nickname):
        return self.account_repository.find_by_nickname(nickname) is None


class SecurityService:
    def __init__(self, account_repository, session_token_repository):
        self.account_repository = account_repository
        self.session_token_repository = session_token_repository

    def generate_auth_token_without_password(self, account_id):
        try:
            account = self._get_account_by_id(account_id)
            session_token = SessionToken(account.id)
            return self.session_token_repository.save(session_token)
        except EntityNotFoundError as e:
            raise AccountNotExistsError(e)

    def authenticate_by_hash(self, hash):
        try:
            return self.session_token_repository.find_by_hash(hash)
        except EntityNotFoundError as e:
            raise InvalidCredentialsError(e)

    def _get_account_by_id(self, account_id):
        account = self.account_repository.find_by_id(account_id)
        if account.is_secured():
            raise SecuredAccountError()
        return account


class BattleService:
    def __init__(self, battle_repository, ship_class_repository,
                 event_dispatcher, battlefield_service):
        self.battle_repository = battle_repository
        self.ship_class_repository = ship_class_repository
        self.event_dispatcher = event_dispatcher
        self.battlefield_service = battlefield_service

    def attack(self, attacker_id):
        if self._is_in_battle(attacker_id):
            raise AlreadyInBattleError()

        battle = self.battle_repository.find_looking_for_opponent_battle(
            attacker_id)
        if battle is not None:
            return self._join_battle(battle, attacker_id)
        return self._start_battle(attacker_id)

    def get_current_battle(self, account_id):
        return (self
                .battle_repository
                .find_ongoing_battle_with_participant(account_id))

    def deploy_ship_for_battle(self, battle_id, account_id, ship):
        try:
            self.ship_class_repository.find_by_id(ship.ship_class)
        except EntityNotFoundError:
            raise InvalidShipClassError()
        battle = self.battle_repository.find_by_id(battle_id)
        if battle.state != BattleState.deploy:
            raise InvalidBattleStateError()
        if not battle.is_participant(account_id):
            raise NotParticipantError
        self.battlefield_service.deploy_ship_on_battlefield(
            battle, account_id, ship)

    def ready_for_battle(self, account_id, battle_id):
        battle = self.battle_repository.find_by_id(battle_id)
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        self.battlefield_service.mark_ready(battlefield.id)
        opponent_battlefield = (self.battlefield_service
                                .get_opponent_battlefield(battle, account_id))
        battlefield = self.battlefield_service.get_my_battlefield(
            battle, account_id)
        if (battlefield.ready_for_battle
                and opponent_battlefield.ready_for_battle):
            battle.state = BattleState.fire_exchange
            self.battle_repository.save(battle)

    def fire(self, battle_id, account_id, coordinates):
        battle = self.battle_repository.find_by_id(battle_id)
        if not battle.state == BattleState.fire_exchange:
            raise InvalidBattleStateError()
        if not account_id == battle.turn_account_id:
            raise InvalidPlayerError()
        defender_id = battle.get_second_account_id(account_id)
        result = self.battlefield_service.fire(
            battle.id,
            defender_id,
            coordinates
        )
        battle.next_player_turn()
        self.battle_repository.save(battle)
        return result

    def _is_in_battle(self, attacker_id):
        battles = (self
                   .battle_repository
                   .find_ongoing_battle_with_participant_count(attacker_id))
        return battles > 0

    def _join_battle(self, battle, attacker_id):
        battle.defender_id = attacker_id
        battle.state = BattleState.deploy
        self.event_dispatcher.dispatch(event.Battle.deploy_finished, battle)
        return self.battle_repository.save(battle)

    def _start_battle(self, attacker_id):
        battle = Battle()
        battle.state = BattleState.looking_for_opponent
        battle.attacker_id = attacker_id
        battle.turn_account_id = attacker_id
        return self.battle_repository.save(battle)


class ShipClassService:
    def __init__(self, ship_class_repository):
        self.ship_class_repository = ship_class_repository

    def get_all(self):
        return self.ship_class_repository.find_all()


class BattlefieldService:
    def __init__(self, battlefield_repository, battlefield_inventory):
        self.battlefield_repository = battlefield_repository
        self.battlefield_inventory = battlefield_inventory

    def create_battlefields_for_battle(self, battle):
        attacker_battlefield = Battlefield(battle.id, battle.attacker_id)
        attacker_battlefield.inventory = copy(self.battlefield_inventory)
        attacker_battlefield = self.battlefield_repository.save(
            attacker_battlefield)

        defender_battlefield = Battlefield(battle.id, battle.defender_id)
        defender_battlefield.inventory = copy(self.battlefield_inventory)
        defender_battlefield = self.battlefield_repository.save(
            defender_battlefield)
        return [attacker_battlefield, defender_battlefield]

    def get_my_battlefield(self, battle, account_id):
        return (self.battlefield_repository
                .find_by_battle_and_account(battle.id, account_id))

    def get_opponent_battlefield(self, battle, account_id):
        second_account_id = battle.get_second_account_id(account_id)
        return (self.battlefield_repository
                .find_by_battle_and_account(battle.id, second_account_id))

    def deploy_ship_on_battlefield(self, battle, account_id, ship):
        battlefield = self.get_my_battlefield(battle, account_id)
        battlefield.deploy(ship)
        return self.battlefield_repository.save(battlefield)

    def mark_ready(self, battlefield_id):
        battlefield = self.battlefield_repository.find_by_id(battlefield_id)
        if not battlefield.all_ships_deployed():
            raise NotAllShipsDeployedError()
        battlefield.ready_for_battle = True
        self.battlefield_repository.save(battlefield)

    def fire(self, battle_id, account_id, coordinates):
        battlefield = (self.battlefield_repository
                       .find_by_battle_and_account(battle_id, account_id))
        fire_result = battlefield.fire(coordinates)
        self.battlefield_repository.save(battlefield)
        return fire_result


class ShipService:
    def __init__(self, ship_repository, ship_class_repository):
        self.ship_repository = ship_repository
        self.ship_class_repository = ship_class_repository

    def create_inventory(self, battlefield_id, inventory_configuration):
        for ship_class_id, count in inventory_configuration.items():
            ship_class = self.ship_class_repository.find_by_id(ship_class_id)
            ship = Ship(ship_class_id, Coordinates(0, 0), ship_class.size,
                        Orientation.vertical)
            ship.battlefield_id = battlefield_id
            for i in range(0, count):
                self.ship_repository.save(ship)


class SecuredAccountError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass


class AccountNotExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


class AlreadyInBattleError(Exception):
    pass


class ValidationError(Exception):
    pass


class InvalidShipClassError(Exception):
    pass


class InvalidBattleStateError(Exception):
    pass


class NotParticipantError(Exception):
    pass


class NotAllShipsDeployedError(Exception):
    pass


class InvalidPlayerError(Exception):
    pass
