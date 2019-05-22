# -*- coding: utf-8 -*-
import logging

from datetime import datetime, timedelta

from graphenecommon.aio.chain import AbstractGrapheneChain

from bitsharesapi.aio.bitsharesnoderpc import BitSharesNodeRPC
from bitsharesbase import operations
from bitsharesbase.account import PublicKey
from bitsharesbase.asset_permissions import asset_permissions, toint

from ..account import Account
from ..amount import Amount
from .asset import Asset
from ..committee import Committee
from ..exceptions import AccountExistsException, KeyAlreadyInStoreException
from .instance import set_shared_blockchain_instance, shared_blockchain_instance
from ..price import Price
from ..storage import get_default_config_store
from ..transactionbuilder import ProposalBuilder, TransactionBuilder
from ..vesting import Vesting
from ..wallet import Wallet
from ..witness import Witness
from ..worker import Worker
from ..htlc import Htlc


log = logging.getLogger(__name__)


class BitShares(AbstractGrapheneChain):
    def define_classes(self):
        from ..blockchainobject import BlockchainObject

        self.wallet_class = Wallet
        self.account_class = Account
        self.rpc_class = BitSharesNodeRPC
        self.default_key_store_app_name = "bitshares"
        self.proposalbuilder_class = ProposalBuilder
        self.transactionbuilder_class = TransactionBuilder
        self.blockchainobject_class = BlockchainObject
