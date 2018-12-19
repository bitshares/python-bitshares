# -*- coding: utf-8 -*-
import hashlib
import sys

from binascii import hexlify, unhexlify

from graphenebase.account import Address as GPHAddress
from graphenebase.account import BrainKey as GPHBrainKey
from graphenebase.account import PasswordKey as GPHPasswordKey
from graphenebase.account import PrivateKey as GPHPrivateKey
from graphenebase.account import PublicKey as GPHPublicKey
from graphenebase.account import Prefix

default_prefix = "BTS"


class PasswordKey(GPHPasswordKey):
    """ This class derives a private key given the account name, the
        role and a password. It leverages the technology of Brainkeys
        and allows people to have a secure private key by providing a
        passphrase only.
    """

    prefix = default_prefix


class BrainKey(GPHBrainKey):
    """Brainkey implementation similar to the graphene-ui web-wallet.

        :param str brainkey: Brain Key
        :param int sequence: Sequence number for consecutive keys

        Keys in Graphene are derived from a seed brain key which is a string of
        16 words out of a predefined dictionary with 49744 words. It is a
        simple single-chain key derivation scheme that is not compatible with
        BIP44 but easy to use.

        Given the brain key, a private key is derived as::

            privkey = SHA256(SHA512(brainkey + " " + sequence))

        Incrementing the sequence number yields a new key that can be
        regenerated given the brain key.
    """

    prefix = default_prefix


class Address(GPHAddress):
    """ Address class

        This class serves as an address representation for Public Keys.

        :param str address: Base58 encoded address (defaults to ``None``)
        :param str pubkey: Base58 encoded pubkey (defaults to ``None``)
        :param str prefix: Network prefix (defaults to ``BTS``)

        Example::

           Address("BTSFN9r6VYzBK8EKtMewfNbfiGCr56pHDBFi")

    """

    prefix = default_prefix


class PublicKey(GPHPublicKey):
    """ This class deals with Public Keys and inherits ``Address``.

        :param str pk: Base58 encoded public key
        :param str prefix: Network prefix (defaults to ``BTS``)

        Example:::

           PublicKey("BTS6UtYWWs3rkZGV8JA86qrgkG6tyFksgECefKE1MiH4HkLD8PFGL")

        .. note:: By default, graphene-based networks deal with **compressed**
                  public keys. If an **uncompressed** key is required, the
                  method ``unCompressed`` can be used::

                      PublicKey("xxxxx").unCompressed()

    """

    prefix = default_prefix


class PrivateKey(GPHPrivateKey):
    """ Derives the compressed and uncompressed public keys and
        constructs two instances of ``PublicKey``:

        :param str wif: Base58check-encoded wif key
        :param str prefix: Network prefix (defaults to ``BTS``)

        Example:::

            PrivateKey("5HqUkGuo62BfcJU5vNhTXKJRXuUi9QSE6jp8C3uBJ2BVHtB8WSd")

        Compressed vs. Uncompressed:

        * ``PrivateKey("w-i-f").pubkey``:
            Instance of ``PublicKey`` using compressed key.
        * ``PrivateKey("w-i-f").pubkey.address``:
            Instance of ``Address`` using compressed key.
        * ``PrivateKey("w-i-f").uncompressed``:
            Instance of ``PublicKey`` using uncompressed key.
        * ``PrivateKey("w-i-f").uncompressed.address``:
            Instance of ``Address`` using uncompressed key.

    """

    prefix = default_prefix
