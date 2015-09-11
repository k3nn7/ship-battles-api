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
        self.password_digest = self._secure_password(password)

    def password_valid(self, password):
        return self.password_digest == self._secure_password(password)

    def _secure_password(self, password):
        # @TODO add hashing and salting
        return password


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
