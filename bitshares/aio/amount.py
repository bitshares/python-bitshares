# -*- coding: utf-8 -*-
from .asset import Asset
from .instance import BlockchainInstance
from graphenecommon.aio.amount import Amount as GrapheneAmount


@BlockchainInstance.inject
class Amount(GrapheneAmount):
    """
    This class deals with Amounts of any asset to simplify dealing with the
    tuple::

        (amount, asset)

    :param list args: Allows to deal with different representations of an amount
    :param float amount: Let's create an instance with a specific amount
    :param str asset: Let's you create an instance with a specific asset (symbol)
    :param bitshares.aio.bitshares.BitShares blockchain_instance: BitShares instance
    :returns: All data required to represent an Amount/Asset
    :rtype: dict
    :raises ValueError: if the data provided is not recognized

    .. code-block:: python

        from bitshares.aio.amount import Amount
        from bitshares.aio.asset import Asset
        a = await Amount("1 USD")
        b = await Amount(1, "USD")
        c = await Amount("20", await Asset("USD"))

    Way to obtain a proper instance:

        * ``args`` can be a string, e.g.:  "1 USD"
        * ``args`` can be a dictionary containing ``amount`` and ``asset_id``
        * ``args`` can be a dictionary containing ``amount`` and ``asset``
        * ``args`` can be a list of a ``float`` and ``str`` (symbol)
        * ``args`` can be a list of a ``float`` and a :class:`bitshares.aio.asset.Asset`
        * ``amount`` and ``asset`` are defined manually

    An instance is a dictionary and comes with the following keys:

        * ``amount`` (float)
        * ``symbol`` (str)
        * ``asset`` (instance of :class:`bitshares.aio.asset.Asset`)
    """

    def define_classes(self):
        from .price import Price

        self.asset_class = Asset
        self.price_class = Price
