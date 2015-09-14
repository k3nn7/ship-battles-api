import webapp
from shipbattles import service
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

    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    webapp.app.battle_service = service.BattleService(
        battle_repository,
        dispatcher
    )
    webapp.app.ship_class_service = service.ShipClassService(
        ship_class_repository
    )
    return app
