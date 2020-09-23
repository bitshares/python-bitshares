# -*- coding: utf-8 -*-
from collections import OrderedDict

from graphenebase.types import (
    Array,
    Bool,
    Bytes,
    Fixed_array,
    Id,
    Int16,
    Int64,
    Map,
    Optional,
    PointInTime,
    Set,
    Static_variant,
    String,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    Varint32,
    Void,
    Ripemd160,
    Sha1,
    Sha256,
    Hash160,
)

from .account import PublicKey
from .objects import (
    AccountCreateExtensions,
    AccountOptions,
    Asset,
    AssetOptions,
    BitAssetOptions,
    CallOrderExtension,
    GrapheneObject,
    Memo,
    ObjectId,
    Operation,
    Permission,
    Price,
    PriceFeed,
    Worker_initializer,
    isArgsThisClass,
    AssertPredicate,
)
from .operationids import operations


default_prefix = "BTS"
class_idmap = {}
class_namemap = {}


def fill_classmaps():
    for name, ind in operations.items():
        classname = name[0:1].upper() + name[1:]
        class_namemap[classname] = ind
        try:
            class_idmap[ind] = globals()[classname]
        except Exception:
            continue


def getOperationClassForId(op_id):
    """Convert an operation id into the corresponding class."""
    return class_idmap[op_id] if op_id in class_idmap else None


def getOperationIdForClass(name):
    """Convert an operation classname into the corresponding id."""
    return class_namemap[name] if name in class_namemap else None


def getOperationNameForId(i):
    """Convert an operation id into the corresponding string."""
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    return "Unknown Operation ID %d" % i


class Transfer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)
            if "memo" in kwargs and kwargs["memo"]:
                if isinstance(kwargs["memo"], dict):
                    kwargs["memo"]["prefix"] = prefix
                    memo = Optional(Memo(**kwargs["memo"]))
                else:
                    memo = Optional(Memo(kwargs["memo"]))
            else:
                memo = Optional(None)
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("from", ObjectId(kwargs["from"], "account")),
                        ("to", ObjectId(kwargs["to"], "account")),
                        ("amount", Asset(kwargs["amount"])),
                        ("memo", memo),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_publish_feed(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("publisher", ObjectId(kwargs["publisher"], "account")),
                        ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
                        ("feed", PriceFeed(kwargs["feed"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if kwargs.get("bitasset_opts"):
                bitasset_opts = Optional(BitAssetOptions(kwargs["bitasset_opts"]))
            else:
                bitasset_opts = Optional(None)
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        ("symbol", String(kwargs["symbol"])),
                        ("precision", Uint8(kwargs["precision"])),
                        ("common_options", AssetOptions(kwargs["common_options"])),
                        ("bitasset_opts", bitasset_opts),
                        (
                            "is_prediction_market",
                            Bool(bool(kwargs["is_prediction_market"])),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "new_issuer" in kwargs:
                raise ValueError(
                    "Cannot change asset_issuer with Asset_update anylonger! (BSIP29)"
                )
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        (
                            "asset_to_update",
                            ObjectId(kwargs["asset_to_update"], "asset"),
                        ),
                        ("new_issuer", Optional(None)),
                        ("new_options", AssetOptions(kwargs["new_options"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_update_bitasset(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        (
                            "asset_to_update",
                            ObjectId(kwargs["asset_to_update"], "asset"),
                        ),
                        ("new_options", BitAssetOptions(kwargs["new_options"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_issue(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            prefix = kwargs.get("prefix", default_prefix)

            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "memo" in kwargs and kwargs["memo"]:
                memo = Optional(Memo(prefix=prefix, **kwargs["memo"]))
            else:
                memo = Optional(None)
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        ("asset_to_issue", Asset(kwargs["asset_to_issue"])),
                        (
                            "issue_to_account",
                            ObjectId(kwargs["issue_to_account"], "account"),
                        ),
                        ("memo", memo),
                        ("extensions", Set([])),
                    ]
                )
            )


class Op_wrapper(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([("op", Operation(kwargs["op"]))]))


class Proposal_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "review_period_seconds" in kwargs:
                review = Optional(Uint32(kwargs["review_period_seconds"]))
            else:
                review = Optional(None)
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "fee_paying_account",
                            ObjectId(kwargs["fee_paying_account"], "account"),
                        ),
                        ("expiration_time", PointInTime(kwargs["expiration_time"])),
                        (
                            "proposed_ops",
                            Array([Op_wrapper(o) for o in kwargs["proposed_ops"]]),
                        ),
                        ("review_period_seconds", review),
                        ("extensions", Set([])),
                    ]
                )
            )


class Proposal_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            for o in [
                "active_approvals_to_add",
                "active_approvals_to_remove",
                "owner_approvals_to_add",
                "owner_approvals_to_remove",
                "key_approvals_to_add",
                "key_approvals_to_remove",
            ]:
                if o not in kwargs:
                    kwargs[o] = []

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "fee_paying_account",
                            ObjectId(kwargs["fee_paying_account"], "account"),
                        ),
                        ("proposal", ObjectId(kwargs["proposal"], "proposal")),
                        (
                            "active_approvals_to_add",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["active_approvals_to_add"]
                                ]
                            ),
                        ),
                        (
                            "active_approvals_to_remove",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["active_approvals_to_remove"]
                                ]
                            ),
                        ),
                        (
                            "owner_approvals_to_add",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["owner_approvals_to_add"]
                                ]
                            ),
                        ),
                        (
                            "owner_approvals_to_remove",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["owner_approvals_to_remove"]
                                ]
                            ),
                        ),
                        (
                            "key_approvals_to_add",
                            Array(
                                [PublicKey(o) for o in kwargs["key_approvals_to_add"]]
                            ),
                        ),
                        (
                            "key_approvals_to_remove",
                            Array(
                                [
                                    PublicKey(o)
                                    for o in kwargs["key_approvals_to_remove"]
                                ]
                            ),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )


class Limit_order_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("seller", ObjectId(kwargs["seller"], "account")),
                        ("amount_to_sell", Asset(kwargs["amount_to_sell"])),
                        ("min_to_receive", Asset(kwargs["min_to_receive"])),
                        ("expiration", PointInTime(kwargs["expiration"])),
                        ("fill_or_kill", Bool(kwargs["fill_or_kill"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Limit_order_cancel(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "fee_paying_account",
                            ObjectId(kwargs["fee_paying_account"], "account"),
                        ),
                        ("order", ObjectId(kwargs["order"], "limit_order")),
                        ("extensions", Set([])),
                    ]
                )
            )


class Call_order_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "funding_account",
                            ObjectId(kwargs["funding_account"], "account"),
                        ),
                        ("delta_collateral", Asset(kwargs["delta_collateral"])),
                        ("delta_debt", Asset(kwargs["delta_debt"])),
                        ("extensions", CallOrderExtension(kwargs["extensions"])),
                    ]
                )
            )


class Asset_fund_fee_pool(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("from_account", ObjectId(kwargs["from_account"], "account")),
                        ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
                        ("amount", Int64(kwargs["amount"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_claim_fees(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        ("amount_to_claim", Asset(kwargs["amount_to_claim"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_claim_pool(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
                        ("amount_to_claim", Asset(kwargs["amount_to_claim"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Override_transfer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "memo" in kwargs:
                memo = Optional(Memo(kwargs["memo"]))
            else:
                memo = Optional(None)
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        ("from", ObjectId(kwargs["from"], "account")),
                        ("to", ObjectId(kwargs["to"], "account")),
                        ("amount", Asset(kwargs["amount"])),
                        ("memo", memo),
                        ("extensions", Set([])),
                    ]
                )
            )


class Account_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("registrar", ObjectId(kwargs["registrar"], "account")),
                        ("referrer", ObjectId(kwargs["referrer"], "account")),
                        ("referrer_percent", Uint16(kwargs["referrer_percent"])),
                        ("name", String(kwargs["name"])),
                        ("owner", Permission(kwargs["owner"], prefix=prefix)),
                        ("active", Permission(kwargs["active"], prefix=prefix)),
                        ("options", AccountOptions(kwargs["options"], prefix=prefix)),
                        ("extensions", AccountCreateExtensions(kwargs["extensions"])),
                    ]
                )
            )


class Account_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)

            if "owner" in kwargs:
                owner = Optional(Permission(kwargs["owner"], prefix=prefix))
            else:
                owner = Optional(None)

            if "active" in kwargs:
                active = Optional(Permission(kwargs["active"], prefix=prefix))
            else:
                active = Optional(None)

            if "new_options" in kwargs:
                options = Optional(AccountOptions(kwargs["new_options"], prefix=prefix))
            else:
                options = Optional(None)

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("owner", owner),
                        ("active", active),
                        ("new_options", options),
                        ("extensions", Set([])),
                    ]
                )
            )


class Account_whitelist(GrapheneObject):
    no_listing = 0  # < No opinion is specified about this account
    white_listed = 1  # < This account is whitelisted, but not blacklisted
    black_listed = 2  # < This account is blacklisted, but not whitelisted
    white_and_black_listed = 3  # < This account is both whitelisted and blacklisted

    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "authorizing_account",
                            ObjectId(kwargs["authorizing_account"], "account"),
                        ),
                        (
                            "account_to_list",
                            ObjectId(kwargs["account_to_list"], "account"),
                        ),
                        ("new_listing", Uint8(kwargs["new_listing"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Vesting_balance_withdraw(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "vesting_balance",
                            ObjectId(kwargs["vesting_balance"], "vesting_balance"),
                        ),
                        ("owner", ObjectId(kwargs["owner"], "account")),
                        ("amount", Asset(kwargs["amount"])),
                    ]
                )
            )


class Account_upgrade(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "account_to_upgrade",
                            ObjectId(kwargs["account_to_upgrade"], "account"),
                        ),
                        (
                            "upgrade_to_lifetime_member",
                            Bool(kwargs["upgrade_to_lifetime_member"]),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )


class Witness_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "new_url" in kwargs and kwargs["new_url"]:
                new_url = Optional(String(kwargs["new_url"]))
            else:
                new_url = Optional(None)

            if "new_signing_key" in kwargs and kwargs["new_signing_key"]:
                new_signing_key = Optional(PublicKey(kwargs["new_signing_key"]))
            else:
                new_signing_key = Optional(None)

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("witness", ObjectId(kwargs["witness"], "witness")),
                        (
                            "witness_account",
                            ObjectId(kwargs["witness_account"], "account"),
                        ),
                        ("new_url", new_url),
                        ("new_signing_key", new_signing_key),
                    ]
                )
            )


class Asset_update_feed_producers(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            kwargs["new_feed_producers"] = sorted(
                kwargs["new_feed_producers"], key=lambda x: float(x.split(".")[2])
            )

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        (
                            "asset_to_update",
                            ObjectId(kwargs["asset_to_update"], "asset"),
                        ),
                        (
                            "new_feed_producers",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["new_feed_producers"]
                                ]
                            ),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )


class Asset_reserve(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("payer", ObjectId(kwargs["payer"], "account")),
                        ("amount_to_reserve", Asset(kwargs["amount_to_reserve"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Worker_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("owner", ObjectId(kwargs["owner"], "account")),
                        ("work_begin_date", PointInTime(kwargs["work_begin_date"])),
                        ("work_end_date", PointInTime(kwargs["work_end_date"])),
                        ("daily_pay", Uint64(kwargs["daily_pay"])),
                        ("name", String(kwargs["name"])),
                        ("url", String(kwargs["url"])),
                        ("initializer", Worker_initializer(kwargs["initializer"])),
                    ]
                )
            )


class Withdraw_permission_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "withdraw_from_account",
                            ObjectId(kwargs["withdraw_from_account"], "account"),
                        ),
                        (
                            "authorized_account",
                            ObjectId(kwargs["authorized_account"], "account"),
                        ),
                        ("withdrawal_limit", Asset(kwargs["withdrawal_limit"])),
                        (
                            "withdrawal_period_sec",
                            Uint32(kwargs["withdrawal_period_sec"]),
                        ),
                        (
                            "periods_until_expiration",
                            Uint32(kwargs["periods_until_expiration"]),
                        ),
                        ("period_start_time", PointInTime(kwargs["period_start_time"])),
                    ]
                )
            )


class Asset_global_settle(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        (
                            "asset_to_settle",
                            ObjectId(kwargs["asset_to_settle"], "asset"),
                        ),
                        ("settle_price", Price(kwargs["settle_price"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Committee_member_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "committee_member_account",
                            ObjectId(kwargs["committee_member_account"], "account"),
                        ),
                        ("url", String(kwargs["url"])),
                    ]
                )
            )


class Custom(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("payer", ObjectId(kwargs["payer"], "account")),
                        (
                            "required_auths",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["required_auths"]
                                ]
                            ),
                        ),
                        ("id", Uint16(kwargs["id"])),
                        ("data", Bytes(kwargs["data"])),
                    ]
                )
            )


class Bid_collateral(GrapheneObject):
    def detail(self, *args, **kwargs):
        # New pygraphene interface!
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("bidder", ObjectId(kwargs["bidder"], "account")),
                ("additional_collateral", Asset(kwargs["additional_collateral"])),
                ("debt_covered", Asset(kwargs["debt_covered"])),
                ("extensions", Set([])),
            ]
        )


class Balance_claim(GrapheneObject):
    def detail(self, *args, **kwargs):
        # New pygraphene interface!
        prefix = kwargs.pop("prefix", default_prefix)
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                (
                    "deposit_to_account",
                    ObjectId(kwargs["deposit_to_account"], "account"),
                ),
                ("balance_to_claim", ObjectId(kwargs["balance_to_claim"], "balance")),
                (
                    "balance_owner_key",
                    PublicKey(kwargs["balance_owner_key"], prefix=prefix),
                ),
                ("total_claimed", Asset(kwargs["total_claimed"])),
            ]
        )


class Asset_settle(GrapheneObject):
    def detail(self, *args, **kwargs):
        # New pygraphene interface!
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("account", ObjectId(kwargs["account"], "account")),
                ("amount", Asset(kwargs["amount"])),
                ("extensions", Set([])),
            ]
        )


class HtlcHash(Static_variant):
    elements = [Ripemd160, Sha1, Sha256, Hash160]

    def __init__(self, o):
        id = o[0]
        if len(self.elements) <= id:
            raise Exception("Unknown HTLC Hashing method")
        data = self.elements[id](o[1])
        super().__init__(data, id)


class Htlc_create(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("from", ObjectId(kwargs["from"], "account")),
                ("to", ObjectId(kwargs["to"], "account")),
                ("amount", Asset(kwargs["amount"])),
                ("preimage_hash", HtlcHash(kwargs["preimage_hash"])),
                ("preimage_size", Uint16(kwargs["preimage_size"])),
                ("claim_period_seconds", Uint32(kwargs["claim_period_seconds"])),
                ("extensions", Set([])),
            ]
        )


class Htlc_redeem(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("htlc_id", ObjectId(kwargs["htlc_id"], "htlc")),
                ("redeemer", ObjectId(kwargs["redeemer"], "account")),
                ("preimage", Bytes(kwargs["preimage"])),
                ("extensions", Set([])),
            ]
        )


class Htlc_extend(GrapheneObject):
    def detail(self, *args, **kwargs):
        return OrderedDict(
            [
                ("fee", Asset(kwargs["fee"])),
                ("htlc_id", ObjectId(kwargs["htlc_id"], "htlc")),
                ("update_issuer", ObjectId(kwargs["update_issuer"], "account")),
                ("seconds_to_add", Uint32(kwargs["seconds_to_add"])),
                ("extensions", Set([])),
            ]
        )


class Asset_update_issuer(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("issuer", ObjectId(kwargs["issuer"], "account")),
                        (
                            "asset_to_update",
                            ObjectId(kwargs["asset_to_update"], "asset"),
                        ),
                        ("new_issuer", ObjectId(kwargs["new_issuer"], "account")),
                        ("extensions", Set([])),
                    ]
                )
            )


class Assert(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        (
                            "fee_paying_account",
                            ObjectId(kwargs["fee_paying_account"], "account"),
                        ),
                        (
                            "predicates",
                            Array([AssertPredicate(o) for o in kwargs["predicates"]]),
                        ),
                        (
                            "required_auths",
                            Array(
                                [
                                    ObjectId(o, "account")
                                    for o in kwargs["required_auths"]
                                ]
                            ),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )

ticket_type_strings = ['liquid', 'lock_180_days', 'lock_360_days', 'lock_720_days', 'lock_forever']

class Ticket_create_operation(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            if isinstance(kwargs["target_type"], int):
                target_type = Varint32(kwargs["target_type"])
            else:
                target_type = Varint32(ticket_type_strings.index(kwargs["target_type"]))

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("target_type", target_type),
                        ("amount", Asset(kwargs["amount"])),
                        ("extensions", Set([])),
                    ]
                )
            )

class Ticket_update_operation(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            if isinstance(kwargs["target_type"], int):
                target_type = Varint32(kwargs["target_type"])
            else:
                target_type = Varint32(ticket_type_strings.index(kwargs["target_type"]))

            if kwargs.get("amount_for_new_target"):
                amount_for_new_target = Optional(Asset(kwargs["amount_for_new_target"]))
            else:
                amount_for_new_target = Optional(None)

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("ticket", ObjectId(kwargs["ticket"], "ticket")),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("target_type", target_type),
                        ("amount_for_new_target", amount_for_new_target),
                        ("extensions", Set([])),
                    ]
                )
            )


class Liquidity_pool_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("asset_a", ObjectId(kwargs["asset_a"], "asset")),
                        ("asset_b", ObjectId(kwargs["asset_b"], "asset")),
                        ("share_asset", ObjectId(kwargs["share_asset"], "asset")),
                        ("taker_fee_percent", Uint16(kwargs["taker_fee_percent"])),
                        ("withdrawal_fee_percent", Uint16(kwargs["withdrawal_fee_percent"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Liquidity_pool_delete(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("pool", ObjectId(kwargs["pool"], "liquidity_pool")),
                        ("extensions", Set([])),
                    ]
                )
            )


class Liquidity_pool_deposit(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("pool", ObjectId(kwargs["pool"], "liquidity_pool")),
                        ("amount_a", Asset(kwargs["amount_a"])),
                        ("amount_b", Asset(kwargs["amount_b"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Liquidity_pool_withdraw(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("pool", ObjectId(kwargs["pool"], "liquidity_pool")),
                        ("share_amount", Asset(kwargs["share_amount"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class Liquidity_pool_exchange(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(
                OrderedDict(
                    [
                        ("fee", Asset(kwargs["fee"])),
                        ("account", ObjectId(kwargs["account"], "account")),
                        ("pool", ObjectId(kwargs["pool"], "liquidity_pool")),
                        ("amount_to_sell", Asset(kwargs["amount_to_sell"])),
                        ("min_to_receive", Asset(kwargs["min_to_receive"])),
                        ("extensions", Set([])),
                    ]
                )
            )


fill_classmaps()
