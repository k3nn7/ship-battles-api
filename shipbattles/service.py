from shipbattles.entity import Account
import time


class AccountService:
    def __init__(self, account_repository):
        self.account_repository = account_repository

    def create_random_account(self):
        nick = 'user%s' % int(time.time())
        account = Account(nick)
        return self.account_repository.save(account)
