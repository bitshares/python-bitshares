# -*- coding: utf-8 -*-
from grapheneapi.aio.api import Api as Aio_Api

from bitsharesbase.chains import known_chains

from ..bitsharesnoderpc import Api as Sync_Api
from .. import exceptions


class Api(Aio_Api, Sync_Api):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class BitSharesNodeRPC(Api):
    def get_network(self):
        """
        Identify the connected network.

        This call returns a dictionary with keys chain_id, core_symbol and prefix
        """
        # Rely on cached chain properties!
        props = self.get_cached_chain_properties()
        chain_id = props["chain_id"]
        for _, v in known_chains.items():
            if v["chain_id"] == chain_id:
                return v
        raise exceptions.UnknownNetworkException(
            "Connecting to unknown network (chain_id: {})!".format(props["chain_id"])
        )

    async def get_account(self, name, **kwargs):
        """
        Get full account details from account name or id.

        :param str name: Account name or account id
        """
        if len(name.split(".")) == 3:
            result = await self.get_objects([name])
            return result[0]
        else:
            return await self.get_account_by_name(name, **kwargs)

    async def get_asset(self, name, **kwargs):
        """
        Get full asset from name of id.

        :param str name: Symbol name or asset id (e.g. 1.3.0)
        """
        if len(name.split(".")) == 3:
            result = await self.get_objects([name], **kwargs)
            return result[0]
        else:
            result = await self.lookup_asset_symbols([name], **kwargs)
            return result[0]

    async def get_object(self, o, **kwargs):
        """
        Get object with id ``o``

        :param str o: Full object id
        """
        result = await self.get_objects([o], **kwargs)
        return result[0]
