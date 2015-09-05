class AccountRepository:
    def __init__(self):
        self.accounts = []

    def save(self, account):
        id = 'is:%d' % len(self.accounts)
        account.id = id
        self.accounts.append(account)
        return account
