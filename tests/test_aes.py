import string
import random
import unittest
import base64
from pprint import pprint
from bitshares.aes import AESCipher


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.aes = AESCipher("Foobar")

    def test_str(self):
        self.assertIsInstance(AESCipher.str_to_bytes("foobar"), bytes)
        self.assertIsInstance(AESCipher.str_to_bytes(b"foobar"), bytes)

    def test_key(self):
        self.assertEqual(
            base64.b64encode(self.aes.key),
            b"6BGBj4DZw8ItV3uoPWGWeI5VO7QIU1u0IQXN/3JqYKs="
        )

    def test_pad(self):
        self.assertEqual(
            base64.b64encode(self.aes._pad(b"123456")),
            b"MTIzNDU2GhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGho="
        )

    def test_unpad(self):
        self.assertEqual(
            self.aes._unpad(base64.b64decode(b"MTIzNDU2GhoaGhoaGhoaGhoaGhoaGhoaGhoaGhoaGho=")),
            b"123456"
        )

    def test_padding(self):
        for n in range(1, 64):
            name = ''.join(random.choice(string.ascii_lowercase) for _ in range(n))
            self.assertEqual(
                self.aes._unpad(self.aes._pad(
                    bytes(name, "utf-8"))),
                bytes(name, "utf-8")
            )

    def test_encdec(self):
        for n in range(1, 16):
            name = ''.join(random.choice(string.ascii_lowercase) for _ in range(64))
            self.assertEqual(
                self.aes.decrypt(self.aes.encrypt(name)),
                name)
