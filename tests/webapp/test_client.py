import webapp
from shipbattles import service, event, listener
from repository import memory
import eventdispatcher
from repository import serializer


def build():
    app = webapp.app.test_client()
    webapp.app.debug = True
    dispatcher = eventdispatcher.Dispatcher()

    account_repository = memory.AccountRepository(
        serializer.AccountSerializer())
    session_token_repository = memory.SessionTokenRepository(
        serializer.SessionTokenSerializer())
    battle_repository = memory.BattleRepository(
        serializer.BattleSerializer())
    webapp.app.ship_class_repository = memory.ShipClassRepository(
        serializer.ShipClassSerializer())
    battlefield_repository = memory.BattlefieldRepository(
        serializer.BattlefieldSerializer())

    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.ship_class_service = service.ShipClassService(
        webapp.app.ship_class_repository
    )
    webapp.app.battlefield_service = service.BattlefieldService(
        battlefield_repository,
        {'id:0': 1, 'id:1': 1}
    )
    webapp.app.battle_service = service.BattleService(
        battle_repository,
        webapp.app.ship_class_repository,
        dispatcher,
        webapp.app.battlefield_service
    )
    dispatcher.register(
        event.Battle.deploy_finished,
        listener.BattleDeployFinishedListener(webapp.app.battlefield_service)
    )
    return app
