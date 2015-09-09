from pymongo import MongoClient
import webapp
from shipbattles import service
from repository import mongo
from repository.mongo import serializer


def main():
    client = MongoClient("mongodb://mongodb:27017")
    db = client.shipbattles

    account_repository = mongo.CrudRepository(
        db.accounts, serializer.AccountSerializer())

    session_token_repository = mongo.SessionTokenRepository(
        db.session_tokens, serializer.SessionTokenSerializer())

    battle_repository = mongo.BattleRepository(
        db.battles, serializer.BattleSerializer()
    )

    webapp.app.debug = True
    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.battle_service = service.BattleService(
        battle_repository
    )
    webapp.app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
