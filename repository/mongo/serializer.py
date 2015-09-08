from shipbattles import entity


class AccountSerializer:
    def serialize(self, account):
        return {
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
            'account_id': session_token.account_id,
            'hash': session_token.hash
        }

    def deserialize(self, data):
        session_token = entity.SessionToken(data['account_id'])
        session_token.hash = data['hash']
        session_token.id = data['_id']
        return session_token
