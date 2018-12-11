# -*- coding: utf-8 -*-
from bitsharesbase.account import PublicKey
from .account import Account
from .instance import BlockchainInstance

from graphenecommon.message import Message as GrapheneMessage, InvalidMessageSignature


@BlockchainInstance.inject
class Message(GrapheneMessage):
    account_class = Account
    publickey_class = PublicKey
