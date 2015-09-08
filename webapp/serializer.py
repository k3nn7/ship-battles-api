import json


def account_serialize(account):
    return json.dumps({
        'id': str(account.id),
        'nick': account.nick
    })


def battle_serialize(battle):
    return json.dumps({
        'id': str(battle.id),
        'state': battle.state.value,
        'attacker_id': battle.attacker_id,
        'defender_id': battle.defender_id
    })
