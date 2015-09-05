import webapp
from shipbattles import service
from repository import memory


def build():
    app = webapp.app.test_client()
    account_repository = memory.CrudRepository()
    session_token_repository = memory.CrudRepository()
    webapp.app.debug = True
    webapp.app.account_service = service.AccountService(
        account_repository
    )
    webapp.app.security_service = service.SecurityService(
        account_repository,
        session_token_repository
    )
    return app
