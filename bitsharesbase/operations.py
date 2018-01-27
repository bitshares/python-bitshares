from collections import OrderedDict
import json
from graphenebase.types import (
    Uint8, Int16, Uint16, Uint32, Uint64,
    Varint32, Int64, String, Bytes, Void,
    Array, PointInTime, Signature, Bool,
    Set, Fixed_array, Optional, Static_variant,
    Map, Id, VoteId
)
from .objects import GrapheneObject, isArgsThisClass
from .account import PublicKey
from .operationids import operations
from .objects import (
    Operation,
    Asset,
    Memo,
    Price,
    PriceFeed,
    Permission,
    AccountOptions,
    BitAssetOptions,
    AssetOptions,
    ObjectId,
    Worker_initializer,
    SpecialAuthority,
    AccountCreateExtensions
)

default_prefix = "BTS"


def getOperationNameForId(i):
    """ Convert an operation id into the corresponding string
    """
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
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('from', ObjectId(kwargs["from"], "account")),
                ('to', ObjectId(kwargs["to"], "account")),
                ('amount', Asset(kwargs["amount"])),
                ('memo', memo),
                ('extensions', Set([])),
            ]))


class Asset_publish_feed(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('publisher', ObjectId(kwargs["publisher"], "account")),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset")),
                ('feed', PriceFeed(kwargs["feed"])),
                ('extensions', Set([])),
            ]))


class Asset_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "bitasset_opts" in kwargs:
                bitasset_opts = Optional(BitAssetOptions(kwargs["bitasset_opts"]))
            else:
                bitasset_opts = Optional(None)
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('symbol', String(kwargs["symbol"])),
                ('precision', Uint8(kwargs["precision"])),
                ('common_options', AssetOptions(kwargs["common_options"])),
                ('bitasset_opts', bitasset_opts),
                ('is_prediction_market', Bool(bool(kwargs['is_prediction_market']))),
                ('extensions', Set([])),
            ]))


class Asset_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            if "new_issuer" in kwargs:
                new_issuer = Optional(ObjectId(kwargs["new_issuer"], "account"))
            else:
                new_issuer = Optional(None)
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('asset_to_update', ObjectId(kwargs["asset_to_update"], "asset")),
                ('new_issuer', new_issuer),
                ('new_options', AssetOptions(kwargs["new_options"])),
                ('extensions', Set([])),
            ]))


class Asset_update_bitasset(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('asset_to_update', ObjectId(kwargs["asset_to_update"], "asset")),
                ('new_options', BitAssetOptions(kwargs["new_options"])),
                ('extensions', Set([])),
            ]))


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
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('asset_to_issue', Asset(kwargs["asset_to_issue"])),
                ('issue_to_account', ObjectId(kwargs["issue_to_account"], "account")),
                ('memo', memo),
                ('extensions', Set([])),
            ]))


class Op_wrapper(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('op', Operation(kwargs["op"])),
            ]))


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
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('fee_paying_account', ObjectId(kwargs["fee_paying_account"], "account")),
                ('expiration_time', PointInTime(kwargs["expiration_time"])),
                ('proposed_ops',
                    Array([Op_wrapper(o) for o in kwargs["proposed_ops"]])),
                ('review_period_seconds', review),
                ('extensions', Set([])),
            ]))


class Proposal_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            for o in ['active_approvals_to_add',
                      'active_approvals_to_remove',
                      'owner_approvals_to_add',
                      'owner_approvals_to_remove',
                      'key_approvals_to_add',
                      'key_approvals_to_remove']:
                if o not in kwargs:
                    kwargs[o] = []

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('fee_paying_account', ObjectId(kwargs["fee_paying_account"], "account")),
                ('proposal', ObjectId(kwargs["proposal"], "proposal")),
                ('active_approvals_to_add',
                    Array([ObjectId(o, "account") for o in kwargs["active_approvals_to_add"]])),
                ('active_approvals_to_remove',
                    Array([ObjectId(o, "account") for o in kwargs["active_approvals_to_remove"]])),
                ('owner_approvals_to_add',
                    Array([ObjectId(o, "account") for o in kwargs["owner_approvals_to_add"]])),
                ('owner_approvals_to_remove',
                    Array([ObjectId(o, "account") for o in kwargs["owner_approvals_to_remove"]])),
                ('key_approvals_to_add',
                    Array([PublicKey(o) for o in kwargs["key_approvals_to_add"]])),
                ('key_approvals_to_remove',
                    Array([PublicKey(o) for o in kwargs["key_approvals_to_remove"]])),
                ('extensions', Set([])),
            ]))


class Limit_order_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('seller', ObjectId(kwargs["seller"], "account")),
                ('amount_to_sell', Asset(kwargs["amount_to_sell"])),
                ('min_to_receive', Asset(kwargs["min_to_receive"])),
                ('expiration', PointInTime(kwargs["expiration"])),
                ('fill_or_kill', Bool(kwargs["fill_or_kill"])),
                ('extensions', Set([])),
            ]))


class Limit_order_cancel(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('fee_paying_account', ObjectId(kwargs["fee_paying_account"], "account")),
                ('order', ObjectId(kwargs["order"], "limit_order")),
                ('extensions', Set([])),
            ]))


class Call_order_update(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('funding_account', ObjectId(kwargs["funding_account"], "account")),
                ('delta_collateral', Asset(kwargs["delta_collateral"])),
                ('delta_debt', Asset(kwargs["delta_debt"])),
                ('extensions', Set([])),
            ]))


class Asset_fund_fee_pool(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('from_account', ObjectId(kwargs["from_account"], "account")),
                ('asset_id', ObjectId(kwargs["asset_id"], "asset")),
                ('amount', Int64(kwargs["amount"])),
                ('extensions', Set([])),
            ]))


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
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('from', ObjectId(kwargs["from"], "account")),
                ('to', ObjectId(kwargs["to"], "account")),
                ('amount', Asset(kwargs["amount"])),
                ('memo', memo),
                ('extensions', Set([])),
            ]))


class Account_create(GrapheneObject):

    def __init__(self, *args, **kwargs):
        # Allow for overwrite of prefix
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            prefix = kwargs.get("prefix", default_prefix)

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('registrar', ObjectId(kwargs["registrar"], "account")),
                ('referrer', ObjectId(kwargs["referrer"], "account")),
                ('referrer_percent', Uint16(kwargs["referrer_percent"])),
                ('name', String(kwargs["name"])),
                ('owner', Permission(kwargs["owner"], prefix=prefix)),
                ('active', Permission(kwargs["active"], prefix=prefix)),
                ('options', AccountOptions(kwargs["options"], prefix=prefix)),
                ('extensions', AccountCreateExtensions(kwargs["extensions"])),
            ]))


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

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('account', ObjectId(kwargs["account"], "account")),
                ('owner', owner),
                ('active', active),
                ('new_options', options),
                ('extensions', Set([])),
            ]))


class Account_whitelist(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('authorizing_account', ObjectId(kwargs["authorizing_account"], "account")),
                ('account_to_list', ObjectId(kwargs["account_to_list"], "account")),
                ('new_listing', Uint8(kwargs["new_listing"])),
                ('extensions', Set([])),
            ]))


class Vesting_balance_withdraw(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('vesting_balance', ObjectId(kwargs["vesting_balance"], "vesting_balance")),
                ('owner', ObjectId(kwargs["owner"], "account")),
                ('amount', Asset(kwargs["amount"])),
            ]))


class Account_upgrade(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
                self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]
            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('account_to_upgrade', ObjectId(kwargs["account_to_upgrade"], "account")),
                ('upgrade_to_lifetime_member', Bool(kwargs["upgrade_to_lifetime_member"])),
                ('extensions', Set([])),
            ]))


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

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('witness', ObjectId(kwargs["witness"], "witness")),
                ('witness_account', ObjectId(kwargs["witness_account"], "account")),
                ('new_url', new_url),
                ('new_signing_key', new_signing_key),
            ]))


class Asset_update_feed_producers(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            kwargs["new_feed_producers"] = sorted(
                kwargs["new_feed_producers"],
                key=lambda x: float(x.split(".")[2]),
            )

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('issuer', ObjectId(kwargs["issuer"], "account")),
                ('asset_to_update', ObjectId(kwargs["asset_to_update"], "asset")),
                ('new_feed_producers',
                    Array([ObjectId(o, "account") for o in kwargs["new_feed_producers"]])),
                ('extensions', Set([])),
            ]))


class Asset_reserve(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('payer', ObjectId(kwargs["payer"], "account")),
                ('amount_to_reserve', Asset(kwargs["amount_to_reserve"])),
                ('extensions', Set([])),
            ]))


class Worker_create(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('owner', ObjectId(kwargs["owner"], "account")),
                ('work_begin_date', PointInTime(kwargs["work_begin_date"])),
                ('work_end_date', PointInTime(kwargs["work_end_date"])),
                ('daily_pay', Uint64(kwargs["daily_pay"])),
                ('name', String(kwargs["name"])),
                ('url', String(kwargs["url"])),
                ('initializer', Worker_initializer(kwargs["initializer"])),
            ]))


class Bid_collateral(GrapheneObject):
    def __init__(self, *args, **kwargs):
        if isArgsThisClass(self, args):
            self.data = args[0].data
        else:
            if len(args) == 1 and len(kwargs) == 0:
                kwargs = args[0]

            super().__init__(OrderedDict([
                ('fee', Asset(kwargs["fee"])),
                ('bidder', ObjectId(kwargs["bidder"], "account")),
                ('additional_collateral', Asset(
                    kwargs["additional_collateral"])),
                ('debt_covered', Asset(kwargs["debt_covered"])),
                ('extensions', Set([])),
            ]))
