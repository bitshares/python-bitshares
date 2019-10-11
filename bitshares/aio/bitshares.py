# -*- coding: utf-8 -*-
import logging

from datetime import datetime, timedelta

from graphenecommon.aio.chain import AbstractGrapheneChain

from bitsharesapi.aio.bitsharesnoderpc import BitSharesNodeRPC
from bitsharesbase import operations
from bitsharesbase.account import PublicKey
from bitsharesbase.asset_permissions import asset_permissions, toint

from .account import Account
from .amount import Amount
from .asset import Asset
from ..committee import Committee
from ..exceptions import AccountExistsException, KeyAlreadyInStoreException
from .instance import set_shared_blockchain_instance, shared_blockchain_instance
from ..price import Price
from ..storage import get_default_config_store
from .transactionbuilder import ProposalBuilder, TransactionBuilder
from ..vesting import Vesting
from .wallet import Wallet
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

    async def create_asset(
        self,
        symbol,
        precision,
        max_supply,
        description="",
        is_bitasset=False,
        is_prediction_market=False,
        market_fee_percent=0,
        max_market_fee=None,
        permissions={
            "charge_market_fee": True,
            "white_list": True,
            "override_authority": True,
            "transfer_restricted": True,
            "disable_force_settle": True,
            "global_settle": True,
            "disable_confidential": True,
            "witness_fed_asset": True,
            "committee_fed_asset": True,
        },
        flags={
            "charge_market_fee": False,
            "white_list": False,
            "override_authority": False,
            "transfer_restricted": False,
            "disable_force_settle": False,
            "global_settle": False,
            "disable_confidential": False,
            "witness_fed_asset": False,
            "committee_fed_asset": False,
        },
        whitelist_authorities=[],
        blacklist_authorities=[],
        whitelist_markets=[],
        blacklist_markets=[],
        bitasset_options={
            "feed_lifetime_sec": 86400,
            "minimum_feeds": 7,
            "force_settlement_delay_sec": 86400,
            "force_settlement_offset_percent": 100,
            "maximum_force_settlement_volume": 50,
            "short_backing_asset": "1.3.0",
            "extensions": [],
        },
        account=None,
        **kwargs
    ):
        """ Create a new asset

            :param str symbol: Asset symbol
            :param int precision: Asset precision
            :param int max_supply: Asset max supply
            :param str description: (optional) Asset description
            :param bool is_bitasset: (optional) True = bitasset, False = UIA (default:
                False)
            :param bool is_prediction_market: (optional) True: PD, False = plain
                smartcoin (default: False)
            :param float market_fee_percent: (optional) Charge market fee (0-100)
                (default: 0)
            :param float max_market_fee: (optional) Absolute amount of max
                market fee, value of this option should be a whole number (default:
                same as max_supply)
            :param dict permissions: (optional) Asset permissions
            :param dict flags: (optional) Enabled asset flags
            :param list whitelist_authorities: (optional) List of accounts that
                serve as whitelist authorities
            :param list blacklist_authorities: (optional) List of accounts that
                serve as blacklist authorities
            :param list whitelist_markets: (optional) List of assets to allow
                trading with
            :param list blacklist_markets: (optional) List of assets to prevent
                trading with
            :param dict bitasset_options: (optional) Bitasset settings
            :param str account: (optional) the issuer account
                to (defaults to ``default_account``)
        """

        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = await Account(account, blockchain_instance=self)

        if not is_bitasset:
            # Turn off bitasset-specific options
            permissions["disable_force_settle"] = False
            permissions["global_settle"] = False
            permissions["witness_fed_asset"] = False
            permissions["committee_fed_asset"] = False
            bitasset_options = None

        assert set(permissions.keys()).issubset(
            asset_permissions.keys()
        ), "unknown permission"
        assert set(flags.keys()).issubset(asset_permissions.keys()), "unknown flag"
        # Transform permissions and flags into bitmask
        permissions_int = toint(permissions)
        flags_int = toint(flags)

        if not max_market_fee:
            max_market_fee = max_supply

        op = operations.Asset_create(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": account["id"],
                "symbol": symbol,
                "precision": precision,
                "common_options": {
                    "max_supply": int(max_supply * 10 ** precision),
                    "market_fee_percent": int(market_fee_percent * 100),
                    "max_market_fee": int(max_market_fee * 10 ** precision),
                    "issuer_permissions": permissions_int,
                    "flags": flags_int,
                    "core_exchange_rate": {
                        "base": {"amount": 1, "asset_id": "1.3.0"},
                        "quote": {"amount": 1, "asset_id": "1.3.1"},
                    },
                    "whitelist_authorities": [
                        await Account(a, blockchain_instance=self)["id"]
                        for a in whitelist_authorities
                    ],
                    "blacklist_authorities": [
                        await Account(a, blockchain_instance=self)["id"]
                        for a in blacklist_authorities
                    ],
                    "whitelist_markets": [
                        await Asset(a, blockchain_instance=self)["id"]
                        for a in whitelist_markets
                    ],
                    "blacklist_markets": [
                        await Asset(a, blockchain_instance=self)["id"]
                        for a in blacklist_markets
                    ],
                    "description": description,
                    "extensions": [],
                },
                "bitasset_opts": bitasset_options,
                "is_prediction_market": is_prediction_market,
                "extensions": [],
            }
        )

        return await self.finalizeOp(op, account, "active", **kwargs)

    async def cancel(self, orderNumbers, account=None, **kwargs):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumbers". An order number takes the form
            ``1.7.xxx``.

            :param str orderNumbers: The Order Object ide of the form
                ``1.7.xxxx``
        """
        if not account:
            if "default_account" in self.config:
                account = self.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = await Account(account, full=False, blockchain_instance=self)

        if not isinstance(orderNumbers, (list, set, tuple)):
            orderNumbers = {orderNumbers}

        op = []
        for order in orderNumbers:
            op.append(
                operations.Limit_order_cancel(
                    **{
                        "fee": {"amount": 0, "asset_id": "1.3.0"},
                        "fee_paying_account": account["id"],
                        "order": order,
                        "extensions": [],
                        "prefix": self.prefix,
                    }
                )
            )
        return await self.finalizeOp(op, account["name"], "active", **kwargs)
