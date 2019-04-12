# -*- coding: utf-8 -*-
#: Operation ids
ops = [
    "transfer",
    "limit_order_create",
    "limit_order_cancel",
    "call_order_update",
    "fill_order",
    "account_create",
    "account_update",
    "account_whitelist",
    "account_upgrade",
    "account_transfer",
    "asset_create",
    "asset_update",
    "asset_update_bitasset",
    "asset_update_feed_producers",
    "asset_issue",
    "asset_reserve",
    "asset_fund_fee_pool",
    "asset_settle",
    "asset_global_settle",
    "asset_publish_feed",
    "witness_create",
    "witness_update",
    "proposal_create",
    "proposal_update",
    "proposal_delete",
    "withdraw_permission_create",
    "withdraw_permission_update",
    "withdraw_permission_claim",
    "withdraw_permission_delete",
    "committee_member_create",
    "committee_member_update",
    "committee_member_update_global_parameters",
    "vesting_balance_create",
    "vesting_balance_withdraw",
    "worker_create",
    "custom",
    "assert",
    "balance_claim",
    "override_transfer",
    "transfer_to_blind",
    "blind_transfer",
    "transfer_from_blind",
    "asset_settle_cancel",
    "asset_claim_fees",
    "fba_distribute",
    "bid_collateral",
    "execute_bid",
    "asset_claim_pool",
    "asset_update_issuer",
    "htlc_create",
    "htlc_redeem",
    "htlc_redeemed",
    "htlc_extend",
    "htlc_refund",
]
operations = {o: ops.index(o) for o in ops}


def getOperationNameForId(i):
    """ Convert an operation id into the corresponding string
    """
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    return "Unknown Operation ID %d" % i


def getOperationName(id: str):
    """ This method returns the name representation of an operation given
        its value as used in the API
    """
    if isinstance(id, str):
        # Some graphene chains (e.g. steem) do not encode the
        # operation_type as id but in its string form
        assert id in operations.keys(), "Unknown operation {}".format(id)
        return id
    elif isinstance(id, int):
        return getOperationNameForId(id)
    else:
        raise ValueError
