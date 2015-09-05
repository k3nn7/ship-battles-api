import unittest
from shipbattles.service import AccountService
from shipbattles.entity import Account
from repository.memory import AccountRepository


class TestAccountService(unittest.TestCase):
    def setUp(self):
        self.account_repository = AccountRepository()
        self.account_service = AccountService(self.account_repository)

    def test_create_account(self):
        account = self.account_service.create_random_account()
        self.assertIsInstance(account, Account)
        self.assertIn('user', account.nick)
        self.assertIsNotNone(account.id)
