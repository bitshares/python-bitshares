asset_permissions = {}
asset_permissions["charge_market_fee"] = 0x01
asset_permissions["white_list"] = 0x02
asset_permissions["override_authority"] = 0x04
asset_permissions["transfer_restricted"] = 0x08
asset_permissions["disable_force_settle"] = 0x10
asset_permissions["global_settle"] = 0x20
asset_permissions["disable_confidential"] = 0x40
asset_permissions["witness_fed_asset"] = 0x80
asset_permissions["committee_fed_asset"] = 0x100


def toint(permissions):
    permissions_int = 0
    for p in permissions:
        if permissions[p]:
            permissions_int += asset_permissions[p]
    return permissions_int


def todict(number):
    r = {}
    for k, v in asset_permissions.items():
        r[k] = bool(number & v)
    return r
