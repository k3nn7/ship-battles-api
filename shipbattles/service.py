from shipbattles.entity import Account, SessionToken
import time


class AccountService:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def create_random_account(self):
        nick = 'user%s' % int(time.time())
        account = Account(nick)
        return self.account_repository.save(account)


class SecurityService:
    def __init__(self, account_repository, session_token_repository):
        self.account_repository = account_repository
        self.session_token_repository = session_token_repository

    def generate_auth_token_without_password(self, account_id):
        try:
            account = self._get_account_by_id(account_id)
            session_token = SessionToken(account.id)
            return self.session_token_repository.save(session_token)
        except EntityNotFoundError as e:
            raise AccountNotExistsError(e)

    def authenticate_by_hash(self, hash):
        try:
            return self.session_token_repository.find_by_hash(hash)
        except EntityNotFoundError as e:
            raise InvalidCredentialsError(e)

    def _get_account_by_id(self, account_id):
        account = self.account_repository.find_by_id(account_id)
        if account.is_secured():
            raise SecuredAccountError()
        return account


class SecuredAccountError(Exception):
    pass


class EntityNotFoundError(Exception):
    pass


class AccountNotExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass
