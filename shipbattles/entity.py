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
    turn_account_id = None

    def get_second_account_id(self, account_id):
        return (self.defender_id if self.attacker_id == account_id
                else self.attacker_id)

    def is_participant(self, account_id):
        return self.attacker_id == account_id or self.defender_id == account_id

    def next_player_turn(self):
        if self.turn_account_id == self.attacker_id:
            self.turn_account_id = self.defender_id
        else:
            self.turn_account_id = self.attacker_id


class BattleState(Enum):
    looking_for_opponent = 1
    deploy = 2
    fire_exchange = 3


class ShipClass:
    def __init__(self, name, size):
        self.id = None
        self.name = name
        self.size = size


class Ship:
    def __init__(self, ship_class, coordinates, size, shots=0):
        self.ship_class = ship_class
        self.coordinates = coordinates
        self.size = size
        self.shots = shots 

    def intersects(self, coordinates):
        if self.coordinates.x == coordinates.x:
            if (coordinates.y >= self.coordinates.y
               and coordinates.y <= (self.coordinates.y + 1)):
                return True
        return False

    def fire(self):
        self.shots += 1
        if self.shots >= self.size:
            return FireResult.sunken
        return FireResult.hit


class Battlefield:
    def __init__(self, battle_id, account_id):
        self.id = None
        self.battle_id = battle_id
        self.account_id = account_id
        self.ships = []
        self.inventory = []
        self.ready_for_battle = False
        self.shots = []

    def deploy(self, ship):
        if ship.ship_class not in self.inventory.keys():
            raise ShipNotInInventoryError()
        if self.inventory[ship.ship_class] <= 0:
            raise ShipNotInInventoryError()
        self.inventory[ship.ship_class] -= 1
        self.ships.append(ship)

    def all_ships_deployed(self):
        for count in self.inventory.values():
            if count > 0:
                return False
        return True

    def fire(self, coordinates):
        self.shots.append(coordinates)
        for ship in self.ships:
            if ship.intersects(coordinates):
                return ship.fire()
        return FireResult.miss


class Coordinates:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not self.__class__ == other.__class__:
            return False
        return ((self.x == other.x)
                and (self.y == other.y))


class FireResult(Enum):
    miss = 1
    hit = 2
    sunken = 3


class InvalidPasswordError(Exception):
    pass


class InvalidNicknameError(Exception):
    pass


class ShipNotInInventoryError(Exception):
    pass
