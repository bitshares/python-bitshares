# -*- coding: utf-8 -*-
import json
from graphenecommon.aio.asset import Asset as GrapheneAsset

from bitsharesbase import operations
from bitsharesbase.asset_permissions import (
    asset_permissions,
    force_flag,
    test_permissions,
    todict,
)

from .instance import BlockchainInstance
from ..asset import Asset as SyncAsset


@BlockchainInstance.inject
class Asset(GrapheneAsset, SyncAsset):
    """
    BitShares asset.

    Async version of :class:`bitshares.bitshares.Asset`
    """

    async def __init__(self, *args, **kwargs):
        await super().__init__(*args, **kwargs)

        # Permissions and flags
        self["permissions"] = todict(self["options"].get("issuer_permissions"))
        self["flags"] = todict(self["options"].get("flags"))
        try:
            self["description"] = json.loads(self["options"]["description"])
        except Exception:
            self["description"] = self["options"]["description"]

    @property
    async def max_market_fee(self):

        from .amount import Amount

        return await Amount(
            {"amount": self["options"]["max_market_fee"], "asset_id": self["id"]},
            blockchain_instance=self.blockchain,
        )

    @property
    async def feeds(self):
        from .price import PriceFeed

        await self.ensure_full()
        if not self.is_bitasset:
            return
        r = []
        for feed in self["bitasset_data"]["feeds"]:
            r.append(await PriceFeed(feed, blockchain_instance=self.blockchain))
        return r

    @property
    async def feed(self):
        from .price import PriceFeed

        assert self.is_bitasset
        await self.ensure_full()
        return await PriceFeed(
            self["bitasset_data"]["current_feed"], blockchain_instance=self.blockchain
        )

    @property
    async def calls(self):
        return await self.get_call_orders(10)

    async def get_call_orders(self, limit=100):
        from .price import Price
        from .account import Account
        from .amount import Amount
        from .market import Market

        assert limit <= 100
        assert self.is_bitasset
        await self.ensure_full()
        r = []
        bitasset = self["bitasset_data"]
        settlement_price = await Price(
            bitasset["current_feed"]["settlement_price"],
            blockchain_instance=self.blockchain,
        )
        ret = await self.blockchain.rpc.get_call_orders(self["id"], limit)
        for call in ret[:limit]:
            collateral_amount = await Amount(
                {
                    "amount": call["collateral"],
                    "asset_id": call["call_price"]["base"]["asset_id"],
                },
                blockchain_instance=self.blockchain,
            )
            debt_amount = await Amount(
                {
                    "amount": call["debt"],
                    "asset_id": call["call_price"]["quote"]["asset_id"],
                },
                blockchain_instance=self.blockchain,
            )
            call_price = float(collateral_amount) / (
                float(debt_amount)
                * (bitasset["current_feed"]["maintenance_collateral_ratio"] / 1000)
            )
            market = await Market(
                "{}:{}".format(
                    bitasset["options"]["short_backing_asset"], self["symbol"]
                )
            )
            latest = (await market.ticker())["latest"]
            r.append(
                {
                    "account": await Account(
                        call["borrower"], lazy=True, blockchain_instance=self.blockchain
                    ),
                    "collateral": collateral_amount,
                    "debt": debt_amount,
                    "call_price": call_price,
                    "settlement_price": settlement_price,
                    "ratio": (
                        float(collateral_amount) / float(debt_amount) * float(latest)
                    ),
                }
            )
        return r

    @property
    async def settlements(self):
        return await self.get_settle_orders(10)

    async def get_settle_orders(self, limit=100):
        from .account import Account
        from .amount import Amount
        from ..utils import formatTimeString

        assert limit <= 100
        assert self.is_bitasset
        r = []
        ret = await self.blockchain.rpc.get_settle_orders(self["id"], limit)
        for settle in ret[:limit]:
            r.append(
                {
                    "account": await Account(
                        settle["owner"], lazy=True, blockchain_instance=self.blockchain
                    ),
                    "amount": await Amount(
                        settle["balance"], blockchain_instance=self.blockchain
                    ),
                    "date": formatTimeString(settle["settlement_date"]),
                }
            )
        return r

    async def halt(self):
        """Halt this asset from being moved or traded."""
        from .account import Account

        nullaccount = await Account(
            "null-account",  # We set the null-account
            blockchain_instance=self.blockchain,
        )
        flags = {"white_list": True, "transfer_restricted": True}
        options = self["options"]
        test_permissions(options["issuer_permissions"], flags)
        flags_int = force_flag(options["flags"], flags)
        options.update(
            {
                "flags": flags_int,
                "whitelist_authorities": [nullaccount["id"]],
                "blacklist_authorities": [],
                "whitelist_markets": [self["id"]],
                "blacklist_markets": [],
            }
        )
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def release(
        self,
        whitelist_authorities=None,
        blacklist_authorities=None,
        whitelist_markets=None,
        blacklist_markets=None,
    ):
        """
        Release this asset and allow unrestricted transfer, trading, etc.

        :param list whitelist_authorities: List of accounts that
            serve as whitelist authorities
        :param list blacklist_authorities: List of accounts that
            serve as blacklist authorities
        :param list whitelist_markets: List of assets to allow
            trading with
        :param list blacklist_markets: List of assets to prevent
            trading with
        """
        from .account import Account

        if whitelist_authorities is None:
            whitelist_authorities = []
        if blacklist_authorities is None:
            blacklist_authorities = []
        if whitelist_markets is None:
            whitelist_markets = []
        if blacklist_markets is None:
            blacklist_markets = []

        flags = {"white_list": False, "transfer_restricted": False}
        if whitelist_authorities or blacklist_authorities:
            flags["white_list"] = True
        options = self["options"]
        test_permissions(options["issuer_permissions"], flags)
        flags_int = force_flag(options["flags"], flags)
        options.update(
            {
                "flags": flags_int,
                "whitelist_authorities": [
                    (await Account(a, blockchain_instance=self.blockchain))["id"]
                    for a in whitelist_authorities
                ],
                "blacklist_authorities": [
                    (await Account(a, blockchain_instance=self.blockchain))["id"]
                    for a in blacklist_authorities
                ],
                "whitelist_markets": [
                    (await Asset(a))["id"] for a in whitelist_markets
                ],
                "blacklist_markets": [
                    (await Asset(a))["id"] for a in blacklist_markets
                ],
            }
        )
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def setoptions(self, flags):
        """
        Enable a certain flag.

        Flags:

         * charge_market_fee
         * white_list
         * override_authority
         * transfer_restricted
         * disable_force_settle
         * global_settle
         * disable_confidential
         * witness_fed_asset
         * committee_fed_asset

        :param dict flag: dictionary of flags and boolean
        """
        op = super().setoptions(flags, return_op=True)
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def enableflag(self, flag):
        """
        Enable a certain flag.

        :param str flag: Flag name
        """
        return await self.setoptions({flag: True})

    async def disableflag(self, flag):
        """
        Enable a certain flag.

        :param str flag: Flag name
        """
        return await self.setoptions({flag: False})

    async def seize(self, *args):
        """
        Seize amount from an account and send to another.

        ... note:: This requires the ``override_authority`` to be
                   set for this asset!

        :param bitshares.account.Account from_account: From this account
        :param bitshares.account.Account to_account: To this account
        :param bitshares.amount.Amount amount: Amount to seize
        """
        op = super().seize(*args, return_op=True)
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def add_authorities(self, type, authorities=None):
        """
        Add authorities to an assets white/black list.

        :param str type: ``blacklist`` or ``whitelist``
        :param list authorities: List of authorities (Accounts)
        """
        assert type in ["blacklist", "whitelist"]
        assert isinstance(authorities, (list, set))
        from .account import Account

        if authorities is None:
            authorities = []

        flags = {"white_list": True}
        options = self["options"]
        test_permissions(options["issuer_permissions"], flags)
        flags_int = force_flag(options["flags"], flags)
        options.update({"flags": flags_int})

        accounts = [
            await Account(a, blockchain_instance=self.blockchain) for a in authorities
        ]
        ids = [a["id"] for a in accounts]

        if type == "whitelist":
            options["whitelist_authorities"].extend(ids)
        if type == "blacklist":
            options["blacklist_authorities"].extend(ids)

        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def remove_authorities(self, type, authorities=None):
        """
        Remove authorities from an assets white/black list.

        :param str type: ``blacklist`` or ``whitelist``
        :param list authorities: List of authorities (Accounts)
        """
        assert type in ["blacklist", "whitelist"]
        assert isinstance(authorities, (list, set))
        from .account import Account

        if authorities is None:
            authorities = []

        options = self["options"]

        if type == "whitelist":
            for a in authorities:
                account = await Account(a, blockchain_instance=self.blockchain)
                options["whitelist_authorities"].remove(account["id"])
        if type == "blacklist":
            for a in authorities:
                account = await Account(a, blockchain_instance=self.blockchain)
                options["blacklist_authorities"].remove(account["id"])
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def add_markets(self, type, authorities=None, force_enable=True):
        """
        Add markets to an assets white/black list.

        :param str type: ``blacklist`` or ``whitelist``
        :param list markets: List of markets (assets)
        :param bool force_enable: Force enable ``white_list`` flag
        """
        assert type in ["blacklist", "whitelist"]
        assert isinstance(authorities, (list, set))

        if authorities is None:
            authorities = []

        options = self["options"]
        if force_enable:
            test_permissions(options["issuer_permissions"], {"white_list": True})
            flags_int = force_flag(options["flags"], {"white_list": True})
            options.update({"flags": flags_int})
        else:
            assert test_permissions(
                options["flags"], ["white_list"]
            ), "whitelist feature not enabled"

        assets = [
            await Asset(a, blockchain_instance=self.blockchain) for a in authorities
        ]
        ids = [asset["id"] for asset in assets]

        if type == "whitelist":
            options["whitelist_markets"].extend(ids)
        if type == "blacklist":
            options["blacklist_markets"].extend(ids)
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def remove_markets(self, type, authorities=None):
        """
        Remove markets from an assets white/black list.

        :param str type: ``blacklist`` or ``whitelist``
        :param list markets: List of markets (assets)
        """
        assert type in ["blacklist", "whitelist"]
        assert isinstance(authorities, (list, set))

        if authorities is None:
            authorities = []

        options = self["options"]
        if type == "whitelist":
            for a in authorities:
                asset = await Asset(a, blockchain_instance=self.blockchain)
                options["whitelist_markets"].remove(asset["id"])
        if type == "blacklist":
            for a in authorities:
                asset = await Asset(a, blockchain_instance=self.blockchain)
                options["blacklist_markets"].remove(asset["id"])
        op = operations.Asset_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_options": options,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def set_market_fee(self, percentage_fee, max_market_fee):
        """
        Set trading percentage fee.

        :param float percentage_fee: Percentage of fee
        :param bitshares.amount.Amount max_market_fee: Max Fee
        """
        op = super().set_market_fee(percentage_fee, max_market_fee, return_op=True)
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def update_feed_producers(self, producers):
        """
        Update bitasset feed producers.

        :param list producers: List of accounts that are allowed to produce
             a feed
        """
        assert self.is_bitasset, "Asset needs to be a bitasset/market pegged asset"
        from .account import Account

        accounts = [
            await Account(a, blockchain_instance=self.blockchain) for a in producers
        ]
        ids = [a["id"] for a in accounts]
        op = operations.Asset_update_feed_producers(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_feed_producers": ids,
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active")

    async def change_issuer(self, new_issuer, **kwargs):
        """
        Change asset issuer (needs signing with owner key!)

        :param str new_issuer: account name
        """
        from .account import Account

        new_issuer = await Account(new_issuer, blockchain_instance=self.blockchain)
        op = operations.Asset_update_issuer(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "issuer": self["issuer"],
                "asset_to_update": self["id"],
                "new_issuer": new_issuer["id"],
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "owner", **kwargs)

    async def issue(self, amount, to, memo=None, **kwargs):
        """
        Issue new shares of an asset.

        :param float amount: Amount to issue
        :param str to: Recipient
        :param str memo: (optional) Memo message
        """
        from .memo import Memo
        from .account import Account

        to = await Account(to, blockchain_instance=self.blockchain)
        account = await Account(self["issuer"], blockchain_instance=self.blockchain)
        memoObj = await Memo(
            from_account=account, to_account=to, blockchain_instance=self.blockchain
        )

        # append operation
        op = operations.Asset_issue(
            **{
                "fee": {
                    "amount": 0,
                    "asset_id": "1.3.0",
                },  # Will be filled in automatically
                "issuer": account["id"],  # the Issuer account
                "asset_to_issue": {
                    "amount": int(float(amount) * 10 ** self["precision"]),
                    "asset_id": self["id"],
                },
                "issue_to_account": to["id"],
                "memo": memoObj.encrypt(memo),
                "extensions": [],
            }
        )
        return await self.blockchain.finalizeOp(op, self["issuer"], "active", **kwargs)
