from collections import OrderedDict

from django.contrib.auth.hashers import BasePasswordHasher
from django.utils.crypto import constant_time_compare


class PlainTextPassword(BasePasswordHasher):
    algorithm = "plain"

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert salt == ''
        return f"{self.algorithm}${password}"

    def decode(self, encoded):
        algorithm, plaintext = encoded.split('$', 1)
        assert algorithm == self.algorithm
        return plaintext

    def verify(self, password, encoded):
        return constant_time_compare(password, self.decode(encoded))

    def safe_summary(self, encoded):
        return OrderedDict([
            ('algorithm', self.algorithm),
            ('hash', encoded),
        ])

    def harden_runtime(self, password, encoded):
        pass
