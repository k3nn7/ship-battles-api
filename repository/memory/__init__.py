from shipbattles.service import EntityNotFoundError


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
