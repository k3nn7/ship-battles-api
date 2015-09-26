from shipbattles.service import EntityNotFoundError
from shipbattles.entity import BattleState, ShipClass
from copy import copy


class CrudRepository:
    def __init__(self):
        self.data = {}

    def save(self, item):
        item = copy(item)
        if item.id is None:
            id = 'is:%d' % len(self.data)
            item.id = id
        self.data[item.id] = item
        return item

    def find_by_id(self, item_id):
        try:
            return copy(self.data[item_id])
        except KeyError as e:
            raise EntityNotFoundError(e)

    def find_all(self):
        return self.data.values()


class AccountRepository(CrudRepository):
    def find_by_nickname(self, nickname):
        for account in self.data.values():
            if account.nick == nickname:
                return copy(account)
        return None


class SessionTokenRepository(CrudRepository):
    def find_by_hash(self, hash):
        for item in self.data.values():
            if item.hash == hash:
                return copy(item)
        raise EntityNotFoundError()


class BattleRepository(CrudRepository):
    def find_looking_for_opponent_battle(self, attacker_id):
        for item in self.data.values():
            if item.state == BattleState.looking_for_opponent:
                return copy(item)
        return None

    def find_ongoing_battle_with_participant_count(self, account_id):
        count = 0
        for battle in self.data.values():
            participates = self._participates(account_id, battle)
            in_progress = self._in_progress(battle)
            if participates and in_progress:
                count += 1
        return count

    def find_ongoing_battle_with_participant(self, account_id):
        for battle in self.data.values():
            participates = self._participates(account_id, battle)
            in_progress = self._in_progress(battle)
            if participates and in_progress:
                return copy(battle)
        return None

    def _participates(self, account_id, battle):
        return ((battle.attacker_id == account_id)
                or (battle.defender_id == account_id))

    def _in_progress(self, battle):
        return ((battle.state == BattleState.looking_for_opponent)
                or (battle.state == BattleState.deploy)
                or (battle.state == BattleState.fire_exchange))


class ShipClassRepository(CrudRepository):
    def __init__(self):
        self.data = {}
        self.save(ShipClass('keel', 1))
        self.save(ShipClass('destroyer', 2))


class BattlefieldRepository(CrudRepository):
    def find_by_battle_and_account(self, battle_id, account_id):
        for b in self.data.values():
            if (b.battle_id == battle_id and b.account_id == account_id):
                return copy(b)
        raise EntityNotFoundError()
