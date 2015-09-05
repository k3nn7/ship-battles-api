import unittest
from shipbattles.service import SecurityService, SecuredAccountError
from shipbattles.service import AccountNotExistsError
from repository.memory import CrudRepository
from shipbattles.entity import Account


class TestSecurityService(unittest.TestCase):
    def setUp(self):
        self.account_repository = CrudRepository()
        self.session_token_repository = CrudRepository()
        self.security_service = SecurityService(
            self.account_repository,
            self.session_token_repository
        )

    def test_generate_auth_token_without_password(self):
        account = Account('foo')
        account = self.account_repository.save(account)

        auth_token = (self.security_service
                      .generate_auth_token_without_password(account.id))
        self.assertIsNotNone(auth_token)

    def test_generated_tokens_are_always_different(self):
        account = Account('foo')
        account = self.account_repository.save(account)

        auth_token1 = (self.security_service
                       .generate_auth_token_without_password(account.id))
        auth_token2 = (self.security_service
                       .generate_auth_token_without_password(account.id))
        self.assertNotEqual(auth_token1, auth_token2)

    def test_generate_auth_token_without_password_for_secured_account(self):
        account = Account('foo')
        account.set_password('foobar')
        account = self.account_repository.save(account)

        with self.assertRaises(SecuredAccountError):
            (self.security_service
                 .generate_auth_token_without_password(account.id))

    def test_generate_auth_token_for_not_existing_account(self):
        with self.assertRaises(AccountNotExistsError):
            (self.security_service
                 .generate_auth_token_without_password('foo'))
