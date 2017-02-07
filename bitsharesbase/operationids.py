#: Operation ids
operations = {}
operations["transfer"] = 0
operations["limit_order_create"] = 1
operations["limit_order_cancel"] = 2
operations["call_order_update"] = 3
operations["fill_order"] = 4
operations["account_create"] = 5
operations["account_update"] = 6
operations["account_whitelist"] = 7
operations["account_upgrade"] = 8
operations["account_transfer"] = 9
operations["asset_create"] = 10
operations["asset_update"] = 11
operations["asset_update_bitasset"] = 12
operations["asset_update_feed_producers"] = 13
operations["asset_issue"] = 14
operations["asset_reserve"] = 15
operations["asset_fund_fee_pool"] = 16
operations["asset_settle"] = 17
operations["asset_global_settle"] = 18
operations["asset_publish_feed"] = 19
operations["witness_create"] = 20
operations["witness_update"] = 21
operations["proposal_create"] = 22
operations["proposal_update"] = 23
operations["proposal_delete"] = 24
operations["withdraw_permission_create"] = 25
operations["withdraw_permission_update"] = 26
operations["withdraw_permission_claim"] = 27
operations["withdraw_permission_delete"] = 28
operations["committee_member_create"] = 29
operations["committee_member_update"] = 30
operations["committee_member_update_global_parameters"] = 31
operations["vesting_balance_create"] = 32
operations["vesting_balance_withdraw"] = 33
operations["worker_create"] = 34
operations["custom"] = 35
operations["assert"] = 36
operations["balance_claim"] = 37
operations["override_transfer"] = 38
operations["transfer_to_blind"] = 39
operations["blind_transfer"] = 40
operations["transfer_from_blind"] = 41
operations["asset_settle_cancel"] = 42
operations["asset_claim_fees"] = 43


def getOperationNameForId(i):
    """ Convert an operation id into the corresponding string
    """
    for key in operations:
        if int(operations[key]) is int(i):
            return key
    return "Unknown Operation ID %d" % i
