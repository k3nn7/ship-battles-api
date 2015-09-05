import hashlib
import time


class Account:
    def __init__(self, nick):
        self.id = None
        self.password_digest = None
        self.nick = nick

    def is_secured(self):
        return self.password_digest is not None

    def set_password(self, password):
        # @TODO add hashing and salting
        self.password_digest = password


class SessionToken:
    def __init__(self, account_id):
        self.id = None
        self.account_id = account_id
        self.hash = self._generate_hash()

    def _generate_hash(self):
        random_string = '%s' % time.time()
        return hashlib.md5(random_string.encode()).hexdigest()
