# -*- coding: utf-8 -*-
from bitsharesbase.account import PublicKey
from .account import Account
from .instance import BlockchainInstance

from graphenecommon.message import Message as GrapheneMessage, InvalidMessageSignature


@BlockchainInstance.inject
class Message(GrapheneMessage):
    def define_classes(self):
        self.account_class = Account
        self.publickey_class = PublicKey
