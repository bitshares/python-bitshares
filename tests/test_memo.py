import unittest
import os
from pprint import pprint
from itertools import cycle
from bitsharesbase.account import BrainKey, Address, PublicKey, PrivateKey
from bitsharesbase.memo import (
    get_shared_secret,
    _pad,
    _unpad,
    encode_memo,
    decode_memo
)

test_cases = [
    {'from': 'GPH7FPzbN7hnRk24T3Nh9MYM1xBaF5xyRYu8WtyTrtLoUG8cUtszM',
     'message': '688fe6c97f78ad2d3c5a82d9aa61bc23',
     'nonce': '16332877645293003478',
     'plain': 'I am this!',
     'to': 'GPH6HAMuJRkjGJkj6cZWBbTU13gkUhBep383prqRdExXsZsYTrWT5',
     'wif': '5Jpkeq1jiNE8Pe24GxFWTsyWbcP59Qq4cD7qg3Wgd6JFJqJkoG8'},
    {'from': 'GPH7FPzbN7hnRk24T3Nh9MYM1xBaF5xyRYu8WtyTrtLoUG8cUtszM',
     'message': 'db7ab7dfefee3ffa2394ec438601ceff',
     'nonce': '16332877645293003478',
     'plain': 'Hello World',
     'to': 'GPH6HAMuJRkjGJkj6cZWBbTU13gkUhBep383prqRdExXsZsYTrWT5',
     'wif': '5Jpkeq1jiNE8Pe24GxFWTsyWbcP59Qq4cD7qg3Wgd6JFJqJkoG8'},
    {'from': 'GPH7FPzbN7hnRk24T3Nh9MYM1xBaF5xyRYu8WtyTrtLoUG8cUtszM',
     'message': '01b6616cbd10bdd0743c82c2bd580651f3e852360a739e7d11c45f483871dc45',
     'nonce': '16332877645293003478',
     'plain': 'Daniel Larimer',
     'to': 'GPH6HAMuJRkjGJkj6cZWBbTU13gkUhBep383prqRdExXsZsYTrWT5',
     'wif': '5Jpkeq1jiNE8Pe24GxFWTsyWbcP59Qq4cD7qg3Wgd6JFJqJkoG8'},
    {'from': 'GPH7FPzbN7hnRk24T3Nh9MYM1xBaF5xyRYu8WtyTrtLoUG8cUtszM',
     'message': '24702af49bc82e06eb74a4acd91b18c389b13a6c9850a0fd3f728f486fe6daf4',
     'nonce': '16332877645293003478',
     'plain': 'Thanks you, sir!',
     'to': 'GPH6HAMuJRkjGJkj6cZWBbTU13gkUhBep383prqRdExXsZsYTrWT5',
     'wif': '5Jpkeq1jiNE8Pe24GxFWTsyWbcP59Qq4cD7qg3Wgd6JFJqJkoG8'},
    {'from': 'GPH7FPzbN7hnRk24T3Nh9MYM1xBaF5xyRYu8WtyTrtLoUG8cUtszM',
     'message': '1566da5b57e8e0fd9f530a352812a4197b8113df6495efdb246909c6ee1ffea6',
     'nonce': '16332877645293003478',
     'plain': 'äöüß€@$²³',
     'to': 'GPH6HAMuJRkjGJkj6cZWBbTU13gkUhBep383prqRdExXsZsYTrWT5',
     'wif': '5Jpkeq1jiNE8Pe24GxFWTsyWbcP59Qq4cD7qg3Wgd6JFJqJkoG8'}
]

test_shared_secrets = [
    ["5JYWCqDpeVrefVaFxJfDc3mzQ67dtsfhU7zcB7AMJYuTH57VsoE", "GPH56EzLTXkis55hBsompVXmSdnayG3afDNFmsCLohPh6rSNzkzhs", "fbb2fef5a3a115887df84c694e8ac5c9bf998c89d0c22438c18fd018f2529460"],
    ["5JKhu9ZKydGFz7yGURocDVEepSY9fk2VRGAA8Xnb9wwFWa8yTWy", "GPH818iy2auxecLxhWTtW219w2VAfBYHxeHaeRASoTFLnsZo1DJ63", "4a52093355abeb31cef02ee1cbdf0661d982d52ad8fe39c68957e3ae03f3bda9"],
    ["5KKmTkFCNnedj6hbyRYJwcaMnc4TkuwrPsJDqR2Bj9ShHkfdgQ3", "GPH78SdnBpqhEHxxzwZeKoFEXV6PviymWzBF7ev29pZcTCF8ynJAo", "500e67a07f53d49b88db635c64e4b0a2414168c7054118d40001e86f1abce131"],
    ["5KLBuZtagfmGqhDTEPSM84TXKxKfzNyGaxRKCgdcocEU7Nusw49", "GPH5nYv9AusGXgHyMBbSBV4HyEAmhzXqLNRPvUpKmNpFo5soho95o", "febfa7ad6c48bb0ab976c6416da24017b93a58e4e699dba76fc590b4b1ac0d26"],
    ["5JrVxMdeBZJvWqV4SmyFq9psQ4Dg8cFXtSWDiL7V5gUJC133xC2", "GPH7HxVNixmh33R44Kr2uJERbhvzkaLen8su4juqyFe2FW2U2cCXA", "82ef43913f83dd3ff0b4f06bcd8801a06c9f046b44b054e0a9ad042c28e5bdba"],
    ["5JfEonXJ4H2kSP4V9NzC3uTRtTpLx4wVgDvf5AWN1KKTV6CZ4x7", "GPH6ZtaoP6skA433YGNNJcPGnsgx15psKRBwAy83tw7XWsDy8hso3", "b1ad058e9cc48e305fb46f07736409a55692c67d3507aad6a051b35459ec2f93"],
    ["5J5UDLdk9XjvcbzNY5AQoUB2pttsvN7FtQFyyFZXUUsHFAp9iQd", "GPH51wPrJXWLcX6iNPAoZ9sGk4fHXk6krQgTX1jfuyxtKuhoEan83", "82fcc73de1331913945f6ce6d0207864bbc7cffee10ed3533ab32629cb759323"],
    ["5JNZpagkR8wWsW3n4hHqFUQVkAu3HhJ9kU1criuruFpAwoaesHs", "GPH5SCy1teB91pNYetxEwV8vRyMApsy8aG61wsi8z2B4Zb6kfnqUf", "704097d0c270e93f0ce5fa91049bb0aa2f38ccfc4bdc38840176abbb98337c0c"],
    ["5KKBRfgTgATU5SmF2uy7ewi7BbDDJCtmf3x9CeYziF14uj8YHMM", "GPH7pUa1fp4NtGaRDmZF6TeanHw7zELUp1eWxZasRE3zY4xYKdbhV", "114aba4ab84ea225bbf4b60aaf6d467d3b206ff8a94d531a5a6031ad90c874dd"],
    ["5Jg7muALcVxncN32LyGMDK8zut2b1Sw3VJA1xjZE5ght7DRM9ac", "GPH5Vj6uR2iKmrB2DcFyqNzperycD3a32BBYkefzKYCHoGnXemwWS", "60928672da8e9a7dc0f783f2bf8aaf1b206b9bbd85f0a61b638e0b99f5f8ea56"],
]


class Testcases(unittest.TestCase):

    def test_padding(self):
        for l in range(0, 255):
            s = bytes(l * chr(l), 'utf-8')
            padded = _pad(s, 16).decode('utf-8')
            self.assertEqual(s.decode('utf-8'), _unpad(padded, 16))

    def test_decrypt(self):
        for memo in test_cases:
            dec = decode_memo(PrivateKey(memo["wif"]),
                              PublicKey(memo["to"], prefix="GPH"),
                              memo["nonce"],
                              memo["message"])
            self.assertEqual(memo["plain"], dec)

    def test_encrypt(self):
        for memo in test_cases:
            enc = encode_memo(PrivateKey(memo["wif"]),
                              PublicKey(memo["to"], prefix="GPH"),
                              memo["nonce"],
                              memo["plain"])
            self.assertEqual(memo["message"], enc)

    def test_shared_secret(self):
        for s in test_shared_secrets:
            priv = PrivateKey(s[0])
            pub = PublicKey(s[1], prefix="GPH")
            shared_secret = get_shared_secret(priv, pub)
            self.assertEqual(s[2], shared_secret)

    def test_shared_secrets_equal(self):

        wifs = cycle([x[0] for x in test_shared_secrets])

        for i in range(len(test_shared_secrets)):
            sender_private_key = PrivateKey(next(wifs))
            sender_public_key = sender_private_key.pubkey
            receiver_private_key = PrivateKey(next(wifs))
            receiver_public_key = receiver_private_key.pubkey

            self.assertEqual(
                get_shared_secret(sender_private_key, receiver_public_key),
                get_shared_secret(receiver_private_key, sender_public_key)
            )
