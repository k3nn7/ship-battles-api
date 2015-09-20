import webapp
from shipbattles import service, event, listener
from repository import memory
import eventdispatcher


def build():
    app = webapp.app.test_client()
    webapp.app.debug = True
    dispatcher = eventdispatcher.Dispatcher()

    account_repository = memory.AccountRepository()
    session_token_repository = memory.SessionTokenRepository()
    battle_repository = memory.BattleRepository()
    ship_class_repository = memory.ShipClassRepository()
    battlefield_repository = memory.BattlefieldRepository()

    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.ship_class_service = service.ShipClassService(
        ship_class_repository
    )
    webapp.app.battlefield_service = service.BattlefieldService(
        battlefield_repository,
        {}
    )
    webapp.app.battle_service = service.BattleService(
        battle_repository,
        ship_class_repository,
        dispatcher,
        webapp.app.battlefield_service
    )
    dispatcher.register(
        event.Battle.deploy_finished,
        listener.BattleDeployFinishedListener(webapp.app.battlefield_service)
    )
    return app
