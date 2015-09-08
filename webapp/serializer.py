import json


def account_serialize(account):
    return json.dumps({
        'id': str(account.id),
        'nick': account.nick
    })
