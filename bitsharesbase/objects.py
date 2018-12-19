# -*- coding: utf-8 -*-
import json

from collections import OrderedDict

from graphenebase.objects import GrapheneObject
from graphenebase.objects import Operation as GrapheneOperation
from graphenebase.objects import isArgsThisClass, Asset
from graphenebase.types import Array, Bool, Bytes, Fixed_array, Id, Int16, Int64, Map
from graphenebase.types import ObjectId as GPHObjectId
from graphenebase.types import (
    Optional,
    PointInTime,
    Set,
    Signature,
    Static_variant,
    String,
    Uint8,
    Uint16,
    Uint32,
    Uint64,
    Varint32,
    Void,
    VoteId,
)

from .account import PublicKey
from .objecttypes import object_type
from .operationids import operations


default_prefix = "BTS"


class Operation(GrapheneOperation):
    """ Need to overwrite a few attributes to load proper operations from
        bitshares
    """

    module = "bitsharesbase.operations"
    operations = operations


class ObjectId(GPHObjectId):
    """ Need to overwrite a few attributes to load proper object_types from
        bitshares
    """

    object_types = object_type


def AssetId(asset):
    return ObjectId(asset, "asset")


def AccountId(asset):
    return ObjectId(asset, "account")


class Memo(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.pop("prefix", default_prefix)
            if "message" in kwargs and kwargs["message"]:
                super().__init__(
                    OrderedDict(
                        [
                            ("from", PublicKey(kwargs["from"], prefix=prefix)),
                            ("to", PublicKey(kwargs["to"], prefix=prefix)),
                            ("nonce", Uint64(int(kwargs["nonce"]))),
                            ("message", Bytes(kwargs["message"])),
                        ]
                    )
                )
            else:
                super().__init__(None)


class Price(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [("base", Asset(kwargs["base"])), ("quote", Asset(kwargs["quote"]))]
                )
            )


class PriceFeed(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("settlement_price", Price(kwargs["settlement_price"])),
                        (
                            "maintenance_collateral_ratio",
                            Uint16(kwargs["maintenance_collateral_ratio"]),
                        ),
                        (
                            "maximum_short_squeeze_ratio",
                            Uint16(kwargs["maximum_short_squeeze_ratio"]),
                        ),
                        ("core_exchange_rate", Price(kwargs["core_exchange_rate"])),
                    ]
                )
            )


class Permission(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            prefix = kwargs.pop("prefix", default_prefix)

            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            kwargs["key_auths"] = sorted(
                kwargs["key_auths"],
                key=lambda x: PublicKey(x[0], prefix=prefix),
                reverse=False,
            )
            accountAuths = Map(
                [
                    [ObjectId(e[0], "account"), Uint16(e[1])]
                    for e in kwargs["account_auths"]
                ]
            )
            keyAuths = Map(
                [
                    [PublicKey(e[0], prefix=prefix), Uint16(e[1])]
                    for e in kwargs["key_auths"]
                ]
            )
            super().__init__(
                OrderedDict(
                    [
                        ("weight_threshold", Uint32(int(kwargs["weight_threshold"]))),
                        ("account_auths", accountAuths),
                        ("key_auths", keyAuths),
                        ("extensions", Set([])),
                    ]
                )
            )


class AccountOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        prefix = kwargs.pop("prefix", default_prefix)

        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            # remove dublicates
            kwargs["votes"] = list(set(kwargs["votes"]))
            # Sort votes
            kwargs["votes"] = sorted(
                kwargs["votes"], key=lambda x: float(x.split(":")[1])
            )
            super().__init__(
                OrderedDict(
                    [
                        ("memo_key", PublicKey(kwargs["memo_key"], prefix=prefix)),
                        (
                            "voting_account",
                            ObjectId(kwargs["voting_account"], "account"),
                        ),
                        ("num_witness", Uint16(kwargs["num_witness"])),
                        ("num_committee", Uint16(kwargs["num_committee"])),
                        ("votes", Array([VoteId(o) for o in kwargs["votes"]])),
                        ("extensions", Set([])),
                    ]
                )
            )


class AssetOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("max_supply", Int64(kwargs["max_supply"])),
                        ("market_fee_percent", Uint16(kwargs["market_fee_percent"])),
                        ("max_market_fee", Int64(kwargs["max_market_fee"])),
                        ("issuer_permissions", Uint16(kwargs["issuer_permissions"])),
                        ("flags", Uint16(kwargs["flags"])),
                        ("core_exchange_rate", Price(kwargs["core_exchange_rate"])),
                        (
                            "whitelist_authorities",
                            Array(
                                [
                                    ObjectId(x, "account")
                                    for x in kwargs["whitelist_authorities"]
                                ]
                            ),
                        ),
                        (
                            "blacklist_authorities",
                            Array(
                                [
                                    ObjectId(x, "account")
                                    for x in kwargs["blacklist_authorities"]
                                ]
                            ),
                        ),
                        (
                            "whitelist_markets",
                            Array(
                                [
                                    ObjectId(x, "asset")
                                    for x in kwargs["whitelist_markets"]
                                ]
                            ),
                        ),
                        (
                            "blacklist_markets",
                            Array(
                                [
                                    ObjectId(x, "asset")
                                    for x in kwargs["blacklist_markets"]
                                ]
                            ),
                        ),
                        ("description", String(kwargs["description"])),
                        ("extensions", Set([])),
                    ]
                )
            )


class BitAssetOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("feed_lifetime_sec", Uint32(kwargs["feed_lifetime_sec"])),
                        ("minimum_feeds", Uint8(kwargs["minimum_feeds"])),
                        (
                            "force_settlement_delay_sec",
                            Uint32(kwargs["force_settlement_delay_sec"]),
                        ),
                        (
                            "force_settlement_offset_percent",
                            Uint16(kwargs["force_settlement_offset_percent"]),
                        ),
                        (
                            "maximum_force_settlement_volume",
                            Uint16(kwargs["maximum_force_settlement_volume"]),
                        ),
                        (
                            "short_backing_asset",
                            ObjectId(kwargs["short_backing_asset"], "asset"),
                        ),
                        ("extensions", Set([])),
                    ]
                )
            )


class Worker_initializer(Static_variant):
    def __init__(self, o):
        class Burn_worker_initializer(GrapheneObject):
            def __init__(self, kwargs):
                super().__init__(OrderedDict([]))

        class Refund_worker_initializer(GrapheneObject):
            def __init__(self, kwargs):
                super().__init__(OrderedDict([]))

        class Vesting_balance_worker_initializer(GrapheneObject):
            def __init__(self, *args, **kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(
                        OrderedDict(
                            [
                                (
                                    "pay_vesting_period_days",
                                    Uint16(kwargs["pay_vesting_period_days"]),
                                )
                            ]
                        )
                    )

        id = o[0]
        if id == 0:
            data = Refund_worker_initializer(o[1])
        elif id == 1:
            data = Vesting_balance_worker_initializer(o[1])
        elif id == 2:
            data = Burn_worker_initializer(o[1])
        else:
            raise Exception("Unknown Worker_initializer")
        super().__init__(data, id)


class SpecialAuthority(Static_variant):
    def __init__(self, o):
        class No_special_authority(GrapheneObject):
            def __init__(self, kwargs):
                super().__init__(OrderedDict([]))

        class Top_holders_special_authority(GrapheneObject):
            def __init__(self, kwargs):
                super().__init__(
                    OrderedDict(
                        [
                            ("asset", ObjectId(kwargs["asset"], "asset")),
                            ("num_top_holders", Uint8(kwargs["num_top_holders"])),
                        ]
                    )
                )

        id = o[0]
        if id == 0:
            data = No_special_authority(o[1])
        elif id == 1:
            data = Top_holders_special_authority(o[1])
        else:
            raise Exception("Unknown SpecialAuthority")
        super().__init__(data, id)


class Extension(Array):
    def __init__(self, *args, **kwargs):
        self.json = dict()
        a = []
        for key, value in kwargs.items():
            self.json.update({key: value})
        for arg in args:
            if isinstance(arg, dict):
                self.json.update(arg)

        for index, extension in enumerate(self.sorted_options):
            name = extension[0]
            klass = extension[1]
            for key, value in self.json.items():
                if key.lower() == name.lower():
                    a.append(Static_variant(klass(value), index))
        super().__init__(a)

    def __str__(self):
        """ We overload the __str__ function because the json
            representation is different for extensions
        """
        return json.dumps(self.json)


class AccountCreateExtensions(Extension):
    class Null_ext(GrapheneObject):
        def __init__(self, *args, **kwargs):
            super().__init__(OrderedDict([]))

    class Owner_special_authority(SpecialAuthority):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Active_special_authority(SpecialAuthority):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

    class Buyback_options(GrapheneObject):
        def __init__(self, *args, **kwargs):
            kwargs.update(args[0])
            super().__init__(
                OrderedDict(
                    [
                        ("asset_to_buy", ObjectId(kwargs["asset_to_buy"], "asset")),
                        (
                            "asset_to_buy_issuer",
                            ObjectId(kwargs["asset_to_buy_issuer"], "account"),
                        ),
                        (
                            "markets",
                            Array([ObjectId(x, "asset") for x in kwargs["markets"]]),
                        ),
                    ]
                )
            )

    sorted_options = [
        ("null_ext", Null_ext),
        ("owner_special_authority", Owner_special_authority),
        ("active_special_authority", Active_special_authority),
        ("buyback_options", Buyback_options),
    ]


class CallOrderExtension(Extension):
    def targetCollateralRatio(value):
        if value:
            return Uint16(value)
        else:
            return None

    sorted_options = [("target_collateral_ratio", targetCollateralRatio)]
