# -*- coding: utf-8 -*-
from bitsharesbase.account import PublicKey
from .account import Account
from .instance import BlockchainInstance

from graphenecommon.message import Message as GrapheneMessage, InvalidMessageSignature


@BlockchainInstance.inject
class Message(GrapheneMessage):
    MESSAGE_SPLIT = (
        "-----BEGIN BITSHARES SIGNED MESSAGE-----",
        "-----BEGIN META-----",
        "-----BEGIN SIGNATURE-----",
        "-----END BITSHARES SIGNED MESSAGE-----",
    )

    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey
