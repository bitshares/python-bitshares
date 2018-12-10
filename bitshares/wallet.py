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


class Wallet(GrapheneWallet, BlockchainInstance):
    chaininstance_class = BlockchainInstance
    default_key_store_app_name = "bitshares"
    privatekey_class = PrivateKey
