from shipbattles.entity import Account, SessionToken, Battle, BattleState
from shipbattles.entity import InvalidPasswordError, InvalidNicknameError
import time


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
    def __init__(self, battle_repository):
        self.battle_repository = battle_repository

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

    def _is_in_battle(self, attacker_id):
        battles = (self
                   .battle_repository
                   .find_ongoing_battle_with_participant_count(attacker_id))
        return battles > 0

    def _join_battle(self, battle, attacker_id):
        battle.defender_id = attacker_id
        battle.state = BattleState.deploy
        return self.battle_repository.save(battle)

    def _start_battle(self, attacker_id):
        battle = Battle()
        battle.state = BattleState.looking_for_opponent
        battle.attacker_id = attacker_id
        return self.battle_repository.save(battle)


class ShipClassService:
    def __init__(self, ship_class_repository):
        self.ship_class_repository = ship_class_repository

    def get_all(self):
        return self.ship_class_repository.find_all()


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
