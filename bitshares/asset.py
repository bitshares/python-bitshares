import json
from bitshares.instance import shared_bitshares_instance
from .exceptions import AssetDoesNotExistsException


class Cache(dict):

    cache = dict()


class Asset(dict):

    assets_cache = Cache()

    def __init__(
        self,
        asset,
        lazy=False,
        full=False,
        bitshares_instance=None
    ):
        self.cached = False
        self.full = full
        self.asset = None

        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if isinstance(asset, Asset):
            self.asset = asset.get("symbol")
            super(Asset, self).__init__(asset)
            self.cached = True
            self._cache(asset)
        elif isinstance(asset, str):
            self.asset = asset
            if self.asset in Asset.assets_cache:
                super(Asset, self).__init__(Asset.assets_cache[self.asset])
                self.cached = True
            elif not lazy and not self.cached:
                self.refresh()
                self.cached = True
        else:
            raise ValueError("Asset() expects a symbol, id or an instance of Asset")

    def refresh(self):
        from bitsharesbase import asset_permissions

        asset = self.bitshares.rpc.get_asset(self.asset)
        if not asset:
            raise AssetDoesNotExistsException
        super(Asset, self).__init__(asset)
        if self.full:
            if self.is_bitasset:
                self["bitasset_data"] = self.bitshares.rpc.get_object(asset["bitasset_data_id"])
            self["dynamic_asset_data"] = self.bitshares.rpc.get_object(asset["dynamic_asset_data_id"])

        # Permissions and flags
        self["permissions"] = asset_permissions.todict(asset["options"]["issuer_permissions"])
        self["flags"] = asset_permissions.todict(asset["options"]["flags"])
        try:
            self["description"] = json.loads(asset["options"]["description"])
        except:
            self["description"] = asset["options"]["description"]

        self.cached = True
        self._cache(asset)

    def _cache(self, asset):
        # store in cache
        Asset.assets_cache[asset["symbol"]] = asset

    @property
    def is_bitasset(self):
        return ("bitasset_data_id" in self)

    @property
    def permissions(self):
        return self["permissions"]

    @property
    def flags(self):
        return self["flags"]

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Asset, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Asset, self).items()
