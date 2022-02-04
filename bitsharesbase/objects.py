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
    Ripemd160,
)

from .account import PublicKey
from .objecttypes import object_type
from .operationids import operations


default_prefix = "BTS"

BlockId = Ripemd160


class Operation(GrapheneOperation):
    """Need to overwrite a few attributes to load proper operations from bitshares."""

    module = "bitsharesbase.operations"
    operations = operations


class ObjectId(GPHObjectId):
    """Need to overwrite a few attributes to load proper object_types from bitshares."""

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
            raise ValueError("Unknown {}".format(self.__class__.name))
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
        self.json = {}
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
        """We overload the __str__ function because the json representation is different
        for extensions."""
        return json.dumps(self.json)


class AccountCreateExtensions(Extension):
    class Null_ext(GrapheneObject):
        def __init__(self, *args, **kwargs):
            super().__init__(OrderedDict([]))

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
        ("owner_special_authority", SpecialAuthority),
        ("active_special_authority", SpecialAuthority),
        ("buyback_options", Buyback_options),
    ]


class CallOrderExtension(Extension):
    def targetCollateralRatio(value):
        if value:
            return Uint16(value)
        else:
            return None

    sorted_options = [("target_collateral_ratio", targetCollateralRatio)]


class AssertPredicate(Static_variant):
    def __init__(self, o):
        class Account_name_eq_lit_predicate(GrapheneObject):
            def __init__(self, *args, **kwargs):
                kwargs.update(args[0])
                super().__init__(
                    OrderedDict(
                        [
                            ("account_id", ObjectId(kwargs["account_id"], "account")),
                            ("name", String(kwargs["name"])),
                        ]
                    )
                )

        class Asset_symbol_eq_lit_predicate(GrapheneObject):
            def __init__(self, *args, **kwargs):
                kwargs.update(args[0])
                super().__init__(
                    OrderedDict(
                        [
                            ("asset_id", ObjectId(kwargs["asset_id"], "asset")),
                            ("symbol", String(kwargs["symbol"])),
                        ]
                    )
                )

        class Block_id_predicate(GrapheneObject):
            def __init__(self, *args, **kwargs):
                kwargs.update(args[0])
                super().__init__(OrderedDict([("id", BlockId(kwargs["id"]))]))

        id = o[0]
        if id == 0:
            data = Account_name_eq_lit_predicate(o[1])
        elif id == 1:
            data = Asset_symbol_eq_lit_predicate(o[1])
        elif id == 2:
            data = Block_id_predicate(o[1])
        else:
            raise ValueError("Unknown {}".format(self.__class__.name))
        super().__init__(data, id)


class ChainParameterExtension(Extension):
    class Htlc_options(GrapheneObject):
        def __init__(self, *args, **kwargs):
            super().__init__(
                OrderedDict(
                    [
                        ("max_timeout_secs", Uint32(kwargs["max_timeout_secs"])),
                        ("max_preimage_size", Uint32(kwargs["max_preimage_size"])),
                    ]
                )
            )

    class CustomAuthorityOptions(GrapheneObject):
        def __init__(self, *args, **kwargs):
            kwargs.update(args[0])
            super().__init__(
                OrderedDict(
                    [
                        (
                            "max_custom_authority_lifetime_seconds",
                            Uint32(kwargs["max_custom_authority_lifetime_seconds"]),
                        ),
                        (
                            "max_custom_authorities_per_account",
                            Uint32(kwargs["max_custom_authorities_per_account"]),
                        ),
                        (
                            "max_custom_authorities_per_account_op",
                            Uint32(kwargs["max_custom_authorities_per_account_op"]),
                        ),
                        (
                            "max_custom_authority_restrictions",
                            Uint32(kwargs["max_custom_authority_restrictions"]),
                        ),
                    ]
                )
            )

    def optional_uint16(x):
        if x:
            return Uint16(x)

    sorted_options = [
        ("updatable_htlc_options", Htlc_options),
        ("custom_authority_options", CustomAuthorityOptions),
        ("market_fee_network_percent", optional_uint16),
        ("maker_fee_discount_percent", optional_uint16),
    ]


class ChainParameters(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("block_interval", Uint8(kwargs["block_interval"])),
                        (
                            "maintenance_interval",
                            Uint32(kwargs["maintenance_interval"]),
                        ),  # uint32_t
                        (
                            "maintenance_skip_slots",
                            Uint8(kwargs["maintenance_skip_slots"]),
                        ),  # uint8_t
                        (
                            "committee_proposal_review_period",
                            Uint32(kwargs["committee_proposal_review_period"]),
                        ),  # uint32_t
                        (
                            "maximum_transaction_size",
                            Uint32(kwargs["maximum_transaction_size"]),
                        ),  # uint32_t
                        (
                            "maximum_block_size",
                            Uint32(kwargs["maximum_block_size"]),
                        ),  # uint32_t
                        (
                            "maximum_time_until_expiration",
                            Uint32(kwargs["maximum_time_until_expiration"]),
                        ),  # uint32_t
                        (
                            "maximum_proposal_lifetime",
                            Uint32(kwargs["maximum_proposal_lifetime"]),
                        ),  # uint32_t
                        (
                            "maximum_asset_whitelist_authorities",
                            Uint8(kwargs["maximum_asset_whitelist_authorities"]),
                        ),  # uint8_t
                        (
                            "maximum_asset_feed_publishers",
                            Uint8(kwargs["maximum_asset_feed_publishers"]),
                        ),  # uint8_t
                        (
                            "maximum_witness_count",
                            Uint16(kwargs["maximum_witness_count"]),
                        ),  # uint16_t
                        (
                            "maximum_committee_count",
                            Uint16(kwargs["maximum_committee_count"]),
                        ),  # uint16_t
                        (
                            "maximum_authority_membership",
                            Uint16(kwargs["maximum_authority_membership"]),
                        ),  # uint16_t
                        (
                            "reserve_percent_of_fee",
                            Uint16(kwargs["reserve_percent_of_fee"]),
                        ),  # uint16_t
                        (
                            "network_percent_of_fee",
                            Uint16(kwargs["network_percent_of_fee"]),
                        ),  # uint16_t
                        (
                            "lifetime_referrer_percent_of_fee",
                            Uint16(kwargs["lifetime_referrer_percent_of_fee"]),
                        ),  # uint16_t
                        (
                            "cashback_vesting_period_seconds",
                            Uint32(kwargs["cashback_vesting_period_seconds"]),
                        ),  # uint32_t
                        (
                            "cashback_vesting_threshold",
                            Int64(kwargs["cashback_vesting_threshold"]),
                        ),  # share_type
                        (
                            "count_non_member_votes",
                            Bool(kwargs["count_non_member_votes"]),
                        ),  # bool
                        (
                            "allow_non_member_whitelists",
                            Bool(kwargs["allow_non_member_whitelists"]),
                        ),  # bool
                        (
                            "witness_pay_per_block",
                            Int64(kwargs["witness_pay_per_block"]),
                        ),  # share_type
                        (
                            "witness_pay_vesting_seconds",
                            Uint32(kwargs["witness_pay_vesting_seconds"]),
                        ),  # uint32_t
                        (
                            "worker_budget_per_day",
                            Int64(kwargs["worker_budget_per_day"]),
                        ),  # share_type
                        (
                            "max_predicate_opcode",
                            Uint16(kwargs["max_predicate_opcode"]),
                        ),  # uint16_t
                        (
                            "fee_liquidation_threshold",
                            Int64(kwargs["fee_liquidation_threshold"]),
                        ),  # share_type
                        (
                            "accounts_per_fee_scale",
                            Uint16(kwargs["accounts_per_fee_scale"]),
                        ),  # uint16_t
                        (
                            "account_fee_scale_bitshifts",
                            Uint8(kwargs["account_fee_scale_bitshifts"]),
                        ),  # uint8_t
                        (
                            "max_authority_depth",
                            Uint8(kwargs["max_authority_depth"]),
                        ),  # uint8_t
                        ("extensions", ChainParameterExtension(kwargs["extensions"])),
                    ]
                )
            )


class VestingPolicy(Static_variant):
    def __init__(self, o):
        class Linear_vesting_policy_initializer(GrapheneObject):
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
                                    "begin_timestamp",
                                    PointInTime(kwargs["begin_timestamp"]),
                                ),
                                (
                                    "vesting_cliff_seconds",
                                    Uint32(kwargs["vesting_cliff_seconds"]),
                                ),
                                (
                                    "vesting_duration_seconds",
                                    Uint32(kwargs["vesting_duration_seconds"]),
                                ),
                            ]
                        )
                    )

        class Cdd_vesting_policy_initializer(GrapheneObject):
            def __init__(self, *args, **kwargs):
                if isArgsThisClass(self, args):
                    self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
                    super().__init__(
                        OrderedDict(
                            [
                                ("start_claim", PointInTime(kwargs["start_claim"])),
                                ("vesting_seconds", Uint32(kwargs["vesting_seconds"])),
                            ]
                        )
                    )

        class Instant_vesting_policy_initializer(GrapheneObject):
            def __init__(self, *args, **kwargs):
                super().__init__(OrderedDict([]))

        id = o[0]
        if id == 0:
            data = Linear_vesting_policy_initializer(o[1])
        elif id == 1:
            data = Cdd_vesting_policy_initializer(o[1])
        elif id == 2:
            data = Instant_vesting_policy_initializer(o[1])
        else:
            raise ValueError("Unknown {}".format(self.__class__.name))
        super().__init__(data, id)


class RestrictionArgument(Static_variant):
    def __init__(self, o):
        raise NotImplementedError()

        # TODO: We need to implemented a class for each of these as the content
        # of the static variant is the content of the restriction on this
        # particular type - this will not produce nice code :-(
        graphene_op_restriction_argument_variadic = {
            "void_t",
            "bool",
            "int64_t",
            "string",
            "time_point_sec",
            "public_key_type",
            "fc::sha256",
            "account_id_type",
            "asset_id_type",
            "force_settlement_id_type",
            "committee_member_id_type",
            "witness_id_type",
            "limit_order_id_type",
            "call_order_id_type",
            "custom_id_type",
            "proposal_id_type",
            "withdraw_permission_id_type",
            "vesting_balance_id_type",
            "worker_id_type",
            "balance_id_type",
            "flat_set<bool>",
            "flat_set<int64_t>",
            "flat_set<string>",
            "flat_set<time_point_sec>",
            "flat_set<public_key_type>",
            "flat_set<fc::sha256>",
            "flat_set<account_id_type>",
            "flat_set<asset_id_type>",
            "flat_set<force_settlement_id_type>",
            "flat_set<committee_member_id_type>",
            "flat_set<witness_id_type>",
            "flat_set<limit_order_id_type>",
            "flat_set<call_order_id_type>",
            "flat_set<custom_id_type>",
            "flat_set<proposal_id_type>",
            "flat_set<withdraw_permission_id_type>",
            "flat_set<vesting_balance_id_type>",
            "flat_set<worker_id_type>",
            "flat_set<balance_id_type>",
            "vector<restriction>",
            "vector<vector<restriction>>",
            "variant_assert_argument_type",
        }

        class Argument(GrapheneObject):
            def __init__(self, *args, **kwargs):
                super().__init__(OrderedDict([]))

        id = o[0]
        if len(graphene_op_restriction_argument_variadic) < id:
            raise ValueError("Unknown {}".format(self.__class__.name))
        data = graphene_op_restriction_argument_variadic(id)
        super().__init__(data, id)


class CustomRestriction(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(
                OrderedDict(
                    [
                        ("member_index", Uint32(kwargs["member_index"])),
                        ("restriction_type", Uint32(kwargs["restriction_type"])),
                        ("argument", RestrictionArgument(kwargs["argument"])),
                        ("extensions", Set([])),
                    ]
                )
            )
