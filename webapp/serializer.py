import json


def account_serialize(account):
    return {
        'id': str(account.id),
        'nick': account.nick
    }


def battle_serialize(battle):
    return {
        'id': str(battle.id),
        'state': battle.state.value,
        'attacker_id': (str(battle.attacker_id)
                        if battle.attacker_id is not None else None),
        'defender_id': (str(battle.defender_id)
                        if battle.defender_id is not None else None)
    }


def ship_class_serialize(ship_class):
    return {
        'id': ship_class.id,
        'name': ship_class.name,
        'size': ship_class.size
    }


def my_battlefield_serialize(battlefield):
    return {
        'id': str(battlefield.id),
        'battle_id': str(battlefield.battle_id),
        'account_id': str(battlefield.account_id),
        'ships': collection(battlefield.ships, ship_serialize),
        'inventory': battlefield.inventory,
        'ready_for_battle': battlefield.ready_for_battle,
        'shots': collection(battlefield.shots, shot_serialize)
    }


def ship_serialize(ship):
    return {
        'id': str(ship.ship_class),
        'x': ship.coordinates.x,
        'y': ship.coordinates.y
    }


def shot_serialize(shot):
    return {
        'x': shot.x,
        'y': shot.y
    }


def opponent_battlefield_serialize(battlefield):
    return {
        'id': str(battlefield.id),
        'battle_id': str(battlefield.battle_id),
        'account_id': str(battlefield.account_id),
        'ready_for_battle': battlefield.ready_for_battle,
        'shots': collection(battlefield.shots, shot_serialize)
    }


def collection(collection, item_serialzer):
    return list(map(item_serialzer, collection))


def j(data):
    return json.dumps(data)
