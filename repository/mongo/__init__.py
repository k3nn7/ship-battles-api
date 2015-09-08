from shipbattles.service import EntityNotFoundError


class CrudRepository:
    def __init__(self, collection, serializer_class):
        self.collection = collection
        self.serializer_class = serializer_class

    def save(self, item):
        serialized_item = self.serializer_class.serialize(item)
        result = self.collection.insert_one(serialized_item)
        return self.find_by_id(result.inserted_id)

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
