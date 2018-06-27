import json
from collections import OrderedDict
from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId,
    ObjectId as GPHObjectId
)
from graphenebase.objects import GrapheneObject, isArgsThisClass
from .objecttypes import object_type
from .account import PublicKey
from graphenebase.objects import Operation as GPHOperation
from .operationids import operations
default_prefix = "BTS"


def AssetId(asset):
    return ObjectId(asset, "asset")


def AccountId(asset):
    return ObjectId(asset, "account")


class ObjectId(GPHObjectId):
    """ Encodes object/protocol ids
    """
    def __init__(self, object_str, type_verify=None):
        if len(object_str.split(".")) == 3:
            space, type, id = object_str.split(".")
            self.space = int(space)
            self.type = int(type)
            self.instance = Id(int(id))
            self.Id = object_str
            if type_verify:
                assert object_type[type_verify] == int(type),\
                    "Object id does not match object type! " +\
                    "Excpected %d, got %d" %\
                    (object_type[type_verify], int(type))
        else:
            raise Exception("Object id is invalid")


class Operation(GPHOperation):
    def __init__(self, *args, **kwargs):
        super(Operation, self).__init__(*args, **kwargs)

    def _getklass(self, name):
        module = __import__("bitsharesbase.operations", fromlist=["operations"])
        class_ = getattr(module, name)
        return class_

    def operations(self):
        return operations

    def getOperationNameForId(self, i):
        """ Convert an operation id into the corresponding string
        """
        for key in operations:
            if int(operations[key]) is int(i):
                return key
        return "Unknown Operation ID %d" % i

    def json(self):
        return json.loads(str(self))


class Asset(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('amount', Int64(kwargs["amount"])),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset"))
            ]))


class Memo(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.pop("prefix", default_prefix)
            if "message" in kwargs and kwargs["message"]:
                super().__init__(OrderedDict([
                    ('from', PublicKey(kwargs["from"], prefix=prefix)),
                    ('to', PublicKey(kwargs["to"], prefix=prefix)),
                    ('nonce', Uint64(int(kwargs["nonce"]))),
                    ('message', Bytes(kwargs["message"]))
                ]))
            else:
                super().__init__(None)


class Price(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('base', Asset(kwargs["base"])),
                ('quote', Asset(kwargs["quote"]))
            ]))


class PriceFeed(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('settlement_price', Price(kwargs["settlement_price"])),
                ('maintenance_collateral_ratio', Uint16(kwargs["maintenance_collateral_ratio"])),
                ('maximum_short_squeeze_ratio', Uint16(kwargs["maximum_short_squeeze_ratio"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
            ]))


class Permission(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            prefix = kwargs.pop("prefix", default_prefix)

            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            # Sort keys (FIXME: ideally, the sorting is part of Public
            # Key and not located here)
            kwargs["key_auths"] = sorted(
                kwargs["key_auths"],
                key=lambda x: repr(PublicKey(x[0], prefix=prefix).address),
                reverse=False,
            )
            accountAuths = Map([
                [ObjectId(e[0], "account"), Uint16(e[1])]
                for e in kwargs["account_auths"]
            ])
            keyAuths = Map([
                [PublicKey(e[0], prefix=prefix), Uint16(e[1])]
                for e in kwargs["key_auths"]
            ])
            super().__init__(OrderedDict([
                ('weight_threshold', Uint32(int(kwargs["weight_threshold"]))),
                ('account_auths', accountAuths),
                ('key_auths', keyAuths),
                ('extensions', Set([])),
            ]))


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
                kwargs["votes"],
                key=lambda x: float(x.split(":")[1]),
            )
            super().__init__(OrderedDict([
                ('memo_key', PublicKey(kwargs["memo_key"], prefix=prefix)),
                ('voting_account', ObjectId(kwargs["voting_account"], "account")),
                ('num_witness', Uint16(kwargs["num_witness"])),
                ('num_committee', Uint16(kwargs["num_committee"])),
                ('votes', Array([VoteId(o) for o in kwargs["votes"]])),
                ('extensions', Set([])),
            ]))


class AssetOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('max_supply', Int64(kwargs["max_supply"])),
                ('market_fee_percent', Uint16(kwargs["market_fee_percent"])),
                ('max_market_fee', Int64(kwargs["max_market_fee"])),
                ('issuer_permissions', Uint16(kwargs["issuer_permissions"])),
                ('flags', Uint16(kwargs["flags"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
                ('whitelist_authorities',
                    Array([ObjectId(x, "account") for x in kwargs["whitelist_authorities"]])),
                ('blacklist_authorities',
                    Array([ObjectId(x, "account") for x in kwargs["blacklist_authorities"]])),
                ('whitelist_markets',
                    Array([ObjectId(x, "asset") for x in kwargs["whitelist_markets"]])),
                ('blacklist_markets',
                    Array([ObjectId(x, "asset") for x in kwargs["blacklist_markets"]])),
                ('description', String(kwargs["description"])),
                ('extensions', Set([])),
            ]))


class BitAssetOptions(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('feed_lifetime_sec', Uint32(kwargs["feed_lifetime_sec"])),
                ('minimum_feeds', Uint8(kwargs["minimum_feeds"])),
                ('force_settlement_delay_sec', Uint32(kwargs["force_settlement_delay_sec"])),
                ('force_settlement_offset_percent', Uint16(kwargs["force_settlement_offset_percent"])),
                ('maximum_force_settlement_volume', Uint16(kwargs["maximum_force_settlement_volume"])),
                ('short_backing_asset', ObjectId(kwargs["short_backing_asset"], "asset")),
                ('extensions', Set([])),
            ]))


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
                    super().__init__(OrderedDict([
                        ('pay_vesting_period_days', Uint16(kwargs["pay_vesting_period_days"])),
                    ]))

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
                super().__init__(OrderedDict([
                    ('asset', ObjectId(kwargs["asset"], "asset")),
                    ('num_top_holders', Uint8(kwargs["num_top_holders"])),
                ]))

        id = o[0]
        if id == 0:
            data = No_special_authority(o[1])
        elif id == 1:
            data = Top_holders_special_authority(o[1])
        else:
            raise Exception("Unknown SpecialAuthority")
        super().__init__(data, id)


class Extension(Array):
    def __str__(self):
        """ We overload the __str__ function because the json
            representation is different for extensions
        """
        return json.dumps(self.json)


class AccountCreateExtensions(Extension):
    def __init__(self, *args, **kwargs):
        # Extensions #################################
        class Null_ext(GrapheneObject):
            def __init__(self, kwargs):
                super().__init__(OrderedDict([]))

        class Owner_special_authority(SpecialAuthority):
            def __init__(self, kwargs):
                super().__init__(kwargs)

        class Active_special_authority(SpecialAuthority):
            def __init__(self, kwargs):
                super().__init__(kwargs)

        class Buyback_options(GrapheneObject):
            def __init__(self, kwargs):
                if isArgsThisClass(self, args):
                        self.data = args[0].data
                else:
                    if len(args) == 1 and len(kwargs) == 0:
                        kwargs = args[0]
#                    assert "1.3.0" in kwargs["markets"], "CORE asset must be in 'markets' to pay fees"
                    super().__init__(OrderedDict([
                        ('asset_to_buy', ObjectId(kwargs["asset_to_buy"], "asset")),
                        ('asset_to_buy_issuer', ObjectId(kwargs["asset_to_buy_issuer"], "account")),
                        ('markets', Array([
                            ObjectId(x, "asset") for x in kwargs["markets"]
                        ])),
                    ]))
        # End of Extensions definition ################
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0 and not(isinstance(args[0], list)):
                kwargs = args[0]

        self.json = dict()
        a = []
        sorted_options = [
            "null_ext",
            "owner_special_authority",
            "active_special_authority",
            "buyback_options"
        ]
        sorting = sorted(kwargs.items(), key=lambda x: sorted_options.index(x[0]))
        for key, value in sorting:
            self.json.update({key: value})
            if key == "null_ext":
                a.append(Static_variant(
                    Null_ext({key: value}),
                    sorted_options.index(key))
                )
            elif key == "owner_special_authority":
                a.append(Static_variant(
                    Owner_special_authority(value),
                    sorted_options.index(key))
                )
            elif key == "active_special_authority":
                a.append(Static_variant(
                    Active_special_authority(value),
                    sorted_options.index(key))
                )
            elif key == "buyback_options":
                a.append(Static_variant(
                    Buyback_options(value),
                    sorted_options.index(key))
                )
            else:
                raise NotImplementedError("Extension {} is unknown".format(key))

        super().__init__(a)
