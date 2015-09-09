from shipbattles.service import EntityNotFoundError
from shipbattles.entity import BattleState


class CrudRepository:
    def __init__(self):
        self.data = {}

    def save(self, item):
        if item.id is None:
            id = 'is:%d' % len(self.data)
            item.id = id
        self.data[item.id] = item
        return item

    def find_by_id(self, item_id):
        try:
            return self.data[item_id]
        except KeyError as e:
            raise EntityNotFoundError(e)


class SessionTokenRepository(CrudRepository):
    def find_by_hash(self, hash):
        for item in self.data.values():
            if item.hash == hash:
                return item
        raise EntityNotFoundError()


class BattleRepository(CrudRepository):
    def find_looking_for_opponent_battle(self, attacker_id):
        for item in self.data.values():
            if item.state == BattleState.looking_for_opponent:
                return item
        return None

    def find_ongoing_battle_with_participant_count(self, account_id):
        count = 0
        for battle in self.data.values():
            participates = self._participates(account_id, battle)
            in_progress = self._in_progress(battle)
            if participates and in_progress:
                count += 1
        return count

    def _participates(self, account_id, battle):
        return ((battle.attacker_id == account_id)
                or (battle.defender_id == account_id))

    def _in_progress(self, battle):
        return ((battle.state == BattleState.looking_for_opponent)
                or (battle.state == BattleState.deploy))
