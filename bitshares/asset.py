import json
from bitshares.instance import shared_bitshares_instance
from .exceptions import AssetDoesNotExistsException


class Asset(dict):
    """ Deals with Assets of the network.

        :param str Asset: Symbol name or object id of an asset
        :param bool lazy: Lazy loading
        :param bool full: Also obtain bitasset-data and dynamic asset dat
        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
        :returns: All data of an asset
        :rtype: dict

        .. note:: This class comes with its own caching function to reduce the
                  load on the API server. Instances of this class can be
                  refreshed with ``Asset.refresh()``.
    """

    assets_cache = dict()

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
        """ Refresh the data from the API server
        """
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
        """ Is the asset a :doc:`mpa`?
        """
        return ("bitasset_data_id" in self)

    @property
    def permissions(self):
        """ List the permissions for this asset that the issuer can obtain
        """
        return self["permissions"]

    @property
    def flags(self):
        """ List the permissions that are currently used (flags)
        """
        return self["flags"]

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Asset, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Asset, self).items()
