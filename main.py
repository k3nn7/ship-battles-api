from pymongo import MongoClient
import webapp
import eventdispatcher
from shipbattles import service, event, listener
from repository import mongo, memory
from repository import serializer


def main():
    client = MongoClient("mongodb://mongodb:27017")
    db = client.shipbattles
    dispatcher = eventdispatcher.Dispatcher()

    account_repository = mongo.CrudRepository(
        db.accounts, serializer.AccountSerializer())
    session_token_repository = mongo.SessionTokenRepository(
        db.session_tokens, serializer.SessionTokenSerializer())
    battle_repository = mongo.BattleRepository(
        db.battles, serializer.BattleSerializer()
    )
    ship_class_repository = memory.ShipClassRepository()
    battlefield_repository = mongo.BattlefieldRepository(
        db.battlefields, serializer.BattlefieldSerializer()
    )

    webapp.app.debug = True

    webapp.app.ship_class_repository = ship_class_repository

    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.battlefield_service = service.BattlefieldService(
        battlefield_repository,
        {'is:0': 1, 'is:1': 1}
    )
    webapp.app.battle_service = service.BattleService(
        battle_repository,
        ship_class_repository,
        dispatcher,
        webapp.app.battlefield_service
    )
    webapp.app.ship_class_service = service.ShipClassService(
        ship_class_repository
    )

    dispatcher.register(
        event.Battle.deploy_finished,
        listener.BattleDeployFinishedListener(webapp.app.battlefield_service)
    )

    webapp.app.run(host='0.0.0.0', port=8080)

if __name__ == '__main__':
    main()
