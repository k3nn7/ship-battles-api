import json


def account_serialize(account):
    return json.dumps({
        'id': account.id,
        'nick': account.nick
    })
