from shipbattles.service import EntityNotFoundError
from shipbattles.entity import BattleState, ShipClass


class CrudRepository:
    def __init__(self, serializer_class):
        self.data = {}
        self.serializer_class = serializer_class

    def save(self, item):
        serialized_item = self.serializer_class.serialize(item)
        if serialized_item['_id'] is None:
            return self._create_new(serialized_item)
        return self._update(serialized_item)

    def _create_new(self, serialized_item):
        item_id = 'id:%d' % len(self.data)
        serialized_item['_id'] = item_id
        self.data[item_id] = serialized_item
        return self.find_by_id(item_id)

    def _update(self, serialized_item):
        item_id = serialized_item['_id']
        self.data[item_id] = serialized_item
        return self.find_by_id(item_id)

    def find_by_id(self, item_id):
        try:
            item = self.data[item_id]
            return self.serializer_class.deserialize(item)
        except KeyError as e:
            raise EntityNotFoundError(e)

    def find_all(self):
        items = []
        for item in self.data.values():
            items.append(self.serializer_class.deserialize(item))
        return items


class AccountRepository(CrudRepository):
    def find_by_nickname(self, nickname):
        for account in self.data.values():
            if account['nick'] == nickname:
                return self.serializer_class.deserialize(account)
        return None


class SessionTokenRepository(CrudRepository):
    def find_by_hash(self, hash):
        for item in self.data.values():
            if item['hash'] == hash:
                return self.serializer_class.deserialize(item)
        raise EntityNotFoundError()


class BattleRepository(CrudRepository):
    def find_looking_for_opponent_battle(self, attacker_id):
        for item in self.data.values():
            if item['state'] == BattleState.looking_for_opponent.value:
                return self.serializer_class.deserialize(item)
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
                return self.serializer_class.deserialize(battle)
        return None

    def _participates(self, account_id, battle):
        return ((battle['attacker_id'] == account_id)
                or (battle['defender_id'] == account_id))

    def _in_progress(self, battle):
        return ((battle['state'] == BattleState.looking_for_opponent.value)
                or (battle['state'] == BattleState.deploy.value)
                or (battle['state'] == BattleState.fire_exchange.value))


class ShipClassRepository(CrudRepository):
    def __init__(self, serializer_class):
        super().__init__(serializer_class)
        self.save(ShipClass('keel', 1))
        self.save(ShipClass('destroyer', 2))


class BattlefieldRepository(CrudRepository):
    def find_by_battle_and_account(self, battle_id, account_id):
        for b in self.data.values():
            if (b['battle_id'] == battle_id and b['account_id'] == account_id):
                return self.serializer_class.deserialize(b)
        raise EntityNotFoundError()
