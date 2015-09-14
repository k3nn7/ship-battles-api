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
        'attacker_id': str(battle.attacker_id),
        'defender_id': str(battle.defender_id)
    }


def ship_class_serialize(ship_class):
    return {
        'id': ship_class.id,
        'name': ship_class.name,
        'size': ship_class.size
    }


def collection(collection, item_serialzer):
    return list(map(item_serialzer, collection))


def j(data):
    return json.dumps(data)
