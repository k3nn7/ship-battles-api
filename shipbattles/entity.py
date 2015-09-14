import hashlib
import time
from enum import Enum


class Account:
    def __init__(self, nick):
        self.id = None
        self.password_digest = None
        self.nick = nick

    def is_secured(self):
        return self.password_digest is not None

    def set_password(self, password):
        self._validate_password(password)
        self.password_digest = self._secure_password(password)

    def password_valid(self, password):
        return self.password_digest == self._secure_password(password)

    def set_nickname(self, nickname):
        self._validate_nickname(nickname)
        self.nick = nickname

    def _secure_password(self, password):
        # @TODO add hashing and salting
        return password

    def _validate_password(self, password):
        if not self._is_password_valid(password):
            raise InvalidPasswordError()

    def _is_password_valid(self, password):
        if password in [None, True, False]:
            return False
        if len(password) < 3:
            return False
        return True

    def _validate_nickname(self, nickname):
        if not self._is_nickname_valid(nickname):
            raise InvalidNicknameError()

    def _is_nickname_valid(self, nickname):
        if nickname in [None, True, False]:
            return False
        if len(nickname) < 3:
            return False
        return True


class SessionToken:
    def __init__(self, account_id):
        self.id = None
        self.account_id = account_id
        self.hash = self._generate_hash()

    def _generate_hash(self):
        random_string = '%s' % time.time()
        return hashlib.md5(random_string.encode()).hexdigest()


class Battle:
    id = None
    state = None
    attacker_id = None
    defender_id = None


class BattleState(Enum):
    looking_for_opponent = 1
    deploy = 2


class ShipClass:
    def __init__(self, name, size):
        self.id = None
        self.name = name
        self.size = size


class Battlefield:
    def __init__(self, battle_id, account_id):
        self.id = None
        self.battle_id = battle_id
        self.account_id = account_id


class InvalidPasswordError(Exception):
    pass


class InvalidNicknameError(Exception):
    pass
