from shipbattles.service import EntityNotFoundError
from shipbattles.entity import BattleState


class CrudRepository:
    def __init__(self, collection, serializer_class):
        self.collection = collection
        self.serializer_class = serializer_class

    def save(self, item):
        serialized_item = self.serializer_class.serialize(item)
        if serialized_item['_id'] is None:
            return self._create_new(serialized_item)
        return self._update(serialized_item)

    def _create_new(self, serialized_item):
        del(serialized_item['_id'])
        result = self.collection.insert_one(serialized_item)
        return self.find_by_id(result.inserted_id)

    def _update(self, serialized_item):
        self.collection.replace_one(
            {'_id': serialized_item['_id']},
            serialized_item
        )
        return self.find_by_id(serialized_item['_id'])

    def find_by_id(self, item_id):
        result = self.collection.find_one(item_id)
        if result is None:
            raise EntityNotFoundError()
        return self.serializer_class.deserialize(result)


class SessionTokenRepository(CrudRepository):
    def find_by_hash(self, hash):
        result = self.collection.find_one({"hash": hash})
        if result is None:
            raise EntityNotFoundError()
        return self.serializer_class.deserialize(result)


class BattleRepository(CrudRepository):
    def find_looking_for_opponent_battle(self, attacker_id):
        result = self.collection.find_one({
            "state": BattleState.looking_for_opponent.value
        })
        if result is None:
            return result
        return self.serializer_class.deserialize(result)

    def find_ongoing_battle_with_participant_count(self, account_id):
        query = {
            '$and': [
                {'$or': [
                    {'attacker_id': account_id},
                    {'defender_id': account_id}
                ]},
                {'$or': [
                    {'state': BattleState.looking_for_opponent.value},
                    {'state': BattleState.deploy.value}
                ]}
            ]
        }
        return self.collection.find(query).count()

    def find_ongoing_battle_with_participant(self, account_id):
        query = {
            '$and': [
                {'$or': [
                    {'attacker_id': account_id},
                    {'defender_id': account_id}
                ]},
                {'$or': [
                    {'state': BattleState.looking_for_opponent.value},
                    {'state': BattleState.deploy.value},
                    {'state': BattleState.fire_exchange.value}
                ]}
            ]
        }
        cursor = self.collection.find(query)
        if cursor.count() == 0:
            return None
        return self.serializer_class.deserialize(cursor[0])


class BattlefieldRepository(CrudRepository):
    def find_by_battle_and_account(self, battle_id, account_id):
        query = {
            '$and': [
                {'battle_id': battle_id},
                {'account_id': account_id}
            ]
        }
        cursor = self.collection.find(query)
        if cursor.count() == 0:
            raise EntityNotFoundError()
        return self.serializer_class.deserialize(cursor[0])
