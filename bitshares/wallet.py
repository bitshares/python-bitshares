# -*- coding: utf-8 -*-
from bitsharesbase.account import PrivateKey
from graphenecommon.wallet import Wallet as GrapheneWallet
from graphenecommon.exceptions import (
    InvalidWifError,
    KeyAlreadyInStoreException,
    KeyNotFound,
    NoWalletException,
    OfflineHasNoRPCException,
    WalletExists,
    WalletLocked,
)
from .instance import BlockchainInstance


@BlockchainInstance.inject
class Wallet(GrapheneWallet):
    def define_classes(self):
        # identical to those in bitshares.py!
        self.default_key_store_app_name = "bitshares"
        self.privatekey_class = PrivateKey
