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
from .chains import known_chains
from .objecttypes import object_type
from .account import PublicKey
from graphenebase.objects import Operation as GPHOperation
from .operationids import operations
default_prefix = "BTS"


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
            if "message" in kwargs and kwargs["message"]:
                if "chain" not in kwargs:
                    chain = "BTS"
                else:
                    chain = kwargs["chain"]
                if isinstance(chain, str) and chain in known_chains:
                    chain_params = known_chains[chain]
                elif isinstance(chain, dict):
                    chain_params = chain
                else:
                    raise Exception("Memo() only takes a string or a dict as chain!")
                if "prefix" not in chain_params:
                    raise Exception("Memo() needs a 'prefix' in chain params!")
                prefix = chain_params["prefix"]
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

            # Sorting
            for key in [
                "whitelist_authorities",
                "blacklist_authorities",
                "whitelist_markets",
                "blacklist_markets"
            ]:
                kwargs[key] = sorted(
                    kwargs[key],
                    key=lambda x: int(x.split(".")[-1]),
                )

            super().__init__(OrderedDict([
                ('max_supply', Uint64(kwargs["max_supply"])),
                ('market_fee_percent', Uint16(kwargs["market_fee_percent"])),
                ('max_market_fee', Uint64(kwargs["max_market_fee"])),
                ('issuer_permissions', Uint16(kwargs["issuer_permissions"])),
                ('flags', Uint16(kwargs["flags"])),
                ('core_exchange_rate', Price(kwargs["core_exchange_rate"])),
                ('whitelist_authorities',
                    Array([ObjectId(o, "account") for o in kwargs["whitelist_authorities"]])),
                ('blacklist_authorities',
                    Array([ObjectId(o, "account") for o in kwargs["blacklist_authorities"]])),
                ('whitelist_markets',
                    Array([ObjectId(o, "asset") for o in kwargs["whitelist_markets"]])),
                ('blacklist_markets',
                    Array([ObjectId(o, "asset") for o in kwargs["blacklist_markets"]])),
                ('description', String(kwargs["description"])),
                ('extensions', Set([])),
            ]))
