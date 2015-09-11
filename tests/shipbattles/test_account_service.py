import unittest
from shipbattles.service import AccountService, ValidationError
from shipbattles.entity import Account
from repository.memory import CrudRepository


class TestAccountService(unittest.TestCase):
    def setUp(self):
        self.account_repository = CrudRepository()
        self.account_service = AccountService(self.account_repository)

    def test_create_account(self):
        account = self.account_service.create_random_account()
        self.assertIsInstance(account, Account)
        self.assertIn('user', account.nick)
        self.assertIsNotNone(account.id)

    def test_update_account_password_without_password(self):
        account = self.account_service.create_random_account()
        self.account_service.update_password(account.id, None, 'foo')
        updated_account = self.account_repository.find_by_id(account.id)
        self.assertTrue(updated_account.password_valid('foo'))

    def test_invalid_update_account_password_with_password(self):
        account = self.account_service.create_random_account()
        self.account_service.update_password(account.id, None, 'foo')
        with self.assertRaises(ValidationError):
            self.account_service.update_password(account.id, None, 'bar')

    def test_update_account_password_with_password(self):
        account = self.account_service.create_random_account()
        self.account_service.update_password(account.id, None, 'foo')
        self.account_service.update_password(account.id, 'foo', 'bar')
        updated_account = self.account_repository.find_by_id(account.id)
        self.assertTrue(updated_account.password_valid('bar'))
