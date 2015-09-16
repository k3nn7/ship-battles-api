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
            'defender_id': battle.defender_id
        }

    def deserialize(self, data):
        battle = entity.Battle()
        battle.id = data['_id']
        battle.state = entity.BattleState(data['state'])
        battle.attacker_id = data['attacker_id']
        battle.defender_id = data['defender_id']
        return battle


class BattlefieldSerializer:
    def serialize(self, battlefield):
        return {
            '_id': battlefield.id,
            'battle_id': battlefield.battle_id,
            'account_id': battlefield.account_id
        }

    def deserialize(self, data):
        battlefield = entity.Battlefield(data['battle_id'], data['account_id'])
        battlefield.id = data['_id']
        return battlefield
