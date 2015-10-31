from shipbattles import entity


class AccountSerializer:
    def serialize(self, account):
        return {
            '_id': account.id,
            'password_digest': account.password_digest,
            'nick': account.nick
        }

    def deserialize(self, data):
        account = entity.Account(data['nick'])
        account.password_digest = data['password_digest']
        account.id = data['_id']
        return account


class SessionTokenSerializer:
    def serialize(self, session_token):
        return {
            '_id': session_token.id,
            'account_id': session_token.account_id,
            'hash': session_token.hash
        }

    def deserialize(self, data):
        session_token = entity.SessionToken(data['account_id'])
        session_token.hash = data['hash']
        session_token.id = data['_id']
        return session_token


class BattleSerializer:
    def serialize(self, battle):
        return {
            '_id': battle.id,
            'state': int(battle.state.value),
            'attacker_id': battle.attacker_id,
            'defender_id': battle.defender_id,
            'turn_account_id': battle.turn_account_id,
        }

    def deserialize(self, data):
        battle = entity.Battle()
        battle.id = data['_id']
        battle.state = entity.BattleState(data['state'])
        battle.attacker_id = data['attacker_id']
        battle.defender_id = data['defender_id']
        battle.turn_account_id = data['turn_account_id']
        return battle


class BattlefieldSerializer:
    def serialize(self, battlefield):
        ship_serialize = ShipSerializer()
        coord_serialize = CoordinatesSerializer()
        return {
            '_id': battlefield.id,
            'battle_id': battlefield.battle_id,
            'account_id': battlefield.account_id,
            'ships': serialize_list(battlefield.ships,
                                    ship_serialize.serialize),
            'inventory': battlefield.inventory,
            'ready_for_battle': battlefield.ready_for_battle,
            'shots': serialize_list(battlefield.shots,
                                    coord_serialize.serialize)
        }

    def deserialize(self, data):
        ship_serialize = ShipSerializer()
        coord_serialize = CoordinatesSerializer()
        battlefield = entity.Battlefield(data['battle_id'], data['account_id'])
        battlefield.id = data['_id']
        battlefield.ships = deserialize_list(data['ships'],
                                             ship_serialize.deserialize)
        battlefield.inventory = data['inventory']
        battlefield.ready_for_battle = data['ready_for_battle']
        battlefield.shots = deserialize_list(data['shots'],
                                             coord_serialize.deserialize)
        return battlefield


class CoordinatesSerializer:
    def serialize(self, coordinates):
        return {
            'x': coordinates.x,
            'y': coordinates.y
        }

    def deserialize(self, data):
        return entity.Coordinates(
            data['x'],
            data['y']
        )


class ShipSerializer:
    def serialize(self, ship):
        coordinates_serializer = CoordinatesSerializer()
        return {
            'class': ship.ship_class,
            'coordinates': coordinates_serializer.serialize(ship.coordinates),
            'size': ship.size,
            'shots': ship.shots
        }

    def deserialize(self, data):
        coordinates_serializer = CoordinatesSerializer()
        return entity.Ship(
            data['class'],
            coordinates_serializer.deserialize(data['coordinates']),
            data['size'],
            data['shots']
        )


def serialize_list(collection, item_serialzer):
    return list(map(item_serialzer, collection))


def deserialize_list(collection, item_deserialzer):
    return list(map(item_deserialzer, collection))
