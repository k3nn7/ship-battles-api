import webapp
from shipbattles import service
from repository import memory


def build():
    app = webapp.app.test_client()
    webapp.app.debug = True

    account_repository = memory.CrudRepository()
    session_token_repository = memory.SessionTokenRepository()
    battle_repository = memory.BattleRepository()

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
    return app
