from . import bitshares as bts
from datetime import datetime, timedelta
from .utils import formatTimeFromNow, formatTime, formatTimeString
from .asset import Asset
from .amount import Amount
from .price import Price, Order, FilledOrder
from .account import Account
from bitsharesbase import operations
from bitsharesbase.objects import Operation


class Market(dict):
    def __init__(self, *args, bitshares_instance=None, **kwargs):
        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if len(args) == 1 and isinstance(args[0], str):
            import re
            quote_symbol, base_symbol = re.split("[/-:]", args[0])
            quote = Asset(quote_symbol, bitshares_instance=self.bitshares)
            base = Asset(base_symbol, bitshares_instance=self.bitshares)
            super(Market, self).__init__({"base": base, "quote": quote})

    def returnTicker(self):
        """ Returns the ticker for all markets.

            Output Parameters:

            * ``last``: Price of the order last filled
            * ``lowestAsk``: Price of the lowest ask
            * ``highestBid``: Price of the highest bid
            * ``baseVolume``: Volume of the base asset
            * ``quoteVolume``: Volume of the quote asset
            * ``percentChange``: 24h change percentage (in %)
            * ``settlement_price``: Settlement Price for borrow/settlement
            * ``core_exchange_rate``: Core exchange rate for payment of fee in non-BTS asset
            * ``price24h``: the price 24h ago

            .. note::

                All prices returned by ``returnTicker`` are in the **reveresed**
                orientation as the market. I.e. in the BTC/BTS market, prices are
                BTS per BTC. That way you can multiply prices with `1.05` to
                get a +5%.

                The prices in a `quote`/`base` market is denoted in `base` per
                `quote`:

                    market: USD_BTS - price 300 BTS per USD

            Sample Output:

            .. code-block:: js

                {
                    {
                        "quoteVolume": 48328.73333,
                        "settlement_price": 332.3344827586207,
                        "lowestAsk": 340.0,
                        "baseVolume": 144.1862,
                        "percentChange": -1.9607843231354893,
                        "highestBid": 334.20000000000005,
                        "latest": 333.33333330133934,
                    }
                }

        """
        data = {}
        # Core Exchange rate
        data["core_exchange_rate"] = Price(self["quote"]["options"]["core_exchange_rate"], base=self["base"])

        # smartcoin stuff
        if "bitasset_data_id" in self["quote"]:
            bitasset = self.bitshares.rpc.get_object(self["quote"]["bitasset_data_id"])
            backing_asset_id = bitasset["options"]["short_backing_asset"]
            if backing_asset_id == self["base"]["id"]:
                data["quoteSettlement_price"] = Price(bitasset["current_feed"]["settlement_price"], base=self["base"])
        elif "bitasset_data_id" in self["base"]:
            bitasset = self.bitshares.rpc.get_object(self["base"]["bitasset_data_id"])
            backing_asset_id = bitasset["options"]["short_backing_asset"]
            if backing_asset_id == self["quote"]["id"]:
                data["baseSettlement_price"] = Price(bitasset["current_feed"]["settlement_price"], base=self["base"])

        ticker = self.bitshares.rpc.get_ticker(
            self["base"]["id"],
            self["quote"]["id"],
        )
        data["baseVolume"] = Amount(ticker["base_volume"], self["base"])
        data["quoteVolume"] = Amount(ticker["quote_volume"], self["quote"])
        data["lowestAsk"] = Price(
            ticker["lowest_ask"],
            base=self["base"],
            quote=self["quote"]
        )
        data["highestBid"] = Price(
            ticker["highest_bid"],
            base=self["base"],
            quote=self["quote"]
        )
        data["latest"] = Price(
            ticker["latest"],
            quote=self["quote"],
            base=self["base"],
        )
        data["percentChange"] = round(float(ticker["percent_change"]) * 100, 3)

        return data

    def return24Volume(self):
        """ Returns the 24-hour volume for all markets, plus totals for primary currencies.

            Sample output:

            .. code-block:: js

                {
                    "BTS": 361666.63617,
                    "USD": 1087.0
                }

        """
        volume = self.bitshares.rpc.get_24_volume(
            self["base"]["id"],
            self["quote"]["id"],
        )
        return {
            self["base"]["symbol"]: Amount(volume["base_volume"], self["base"]),
            self["quote"]["symbol"]: Amount(volume["quote_volume"], self["quote"])
        }

    def returnOrderBook(self, limit=25):
        """ Returns the order book for a given market. You may also
            specify "all" to get the orderbooks of all markets.

            :param int limit: Limit the amount of orders (default: 25)

            Sample output:

            .. code-block:: js

                {'bids': [0.003679 USD/BTS (1.9103 USD|519.29602 BTS),
                0.003676 USD/BTS (299.9997 USD|81606.16394 BTS),
                0.003665 USD/BTS (288.4618 USD|78706.21881 BTS),
                0.003665 USD/BTS (3.5285 USD|962.74409 BTS),
                0.003665 USD/BTS (72.5474 USD|19794.41299 BTS)],
                'asks': [0.003738 USD/BTS (36.4715 USD|9756.17339 BTS),
                0.003738 USD/BTS (18.6915 USD|5000.00000 BTS),
                0.003742 USD/BTS (182.6881 USD|48820.22081 BTS),
                0.003772 USD/BTS (4.5200 USD|1198.14798 BTS),
                0.003799 USD/BTS (148.4975 USD|39086.59741 BTS)]}


            .. note:: Each bid is an instance of
                class:`bitshares.price.Order` and thus carries the keys
                ``base``, ``quote`` and ``price``. From those you can
                obtain the actual amounts for sale

        """
        orders = self.bitshares.rpc.get_order_book(
            self["base"]["id"],
            self["quote"]["id"],
            limit
        )
        asks = list(map(lambda x: Order(
            Amount(x["quote"], self["quote"]),
            Amount(x["base"], self["base"])
        ), orders["asks"]))
        bids = list(map(lambda x: Order(
            Amount(x["quote"], self["quote"]),
            Amount(x["base"], self["base"])
        ), orders["bids"]))
        data = {"asks": asks, "bids": bids}
        return data

    def returnOpenOrders(self, account=None):
        """ Returns open Orders
        """
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, bitshares_instance=self.bitshares)

        r = []
        orders = account["limit_orders"]
        for o in orders:
            if ((
                o["sell_price"]["base"]["asset_id"] == self["base"]["id"] and
                o["sell_price"]["quote"]["asset_id"] == self["quote"]["id"]
            ) or (
                o["sell_price"]["base"]["asset_id"] == self["quote"]["id"] and
                o["sell_price"]["quote"]["asset_id"] == self["base"]["id"]
            )):
                r.append(Order(o))
        return r

    def returnOpenOrderIds(self, account=None):
        """ Returns only the ids of open Orders
        """
        return [x["id"] for x in self.returnOpenOrders(account)]

    def returnTrades(self, limit=25, start=None, stop=None):
        """ Returns your trade history for a given market.

            :param int limit: Limit the amount of orders (default: 25)
            :param datetime start: start time
            :param datetime stop: stop time

        """
        # FIXME, this call should also return whether it was a buy or
        # sell
        if not stop:
            stop = datetime.now()
        if not start:
            start = stop - timedelta(hours=24)
        orders = self.bitshares.rpc.get_trade_history(
            self["base"]["symbol"],
            self["quote"]["symbol"],
            formatTime(stop),
            formatTime(start),
            limit)
        return list(map(
            lambda x: FilledOrder(
                x,
                base=self["base"],
                quote=self["quote"]
            ) , orders
        ))

    def returnAccountTrades(self, account=None, limit=25):
        """ Returns your trade history for a given market, specified by
            the "currencyPair" parameter. You may also specify "all" to
            get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)

            Output Parameters:

                - `type`: sell or buy
                - `rate`: price for `quote` denoted in `base` per `quote`
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)

        """
        raise NotImplementedError("This call is not yet fully implemented")
        """
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, bitshares_instance=self.bitshares)
        
        filled = self.bitshares.rpc.get_fill_order_history(
            self["base"]["id"],
            self["quote"]["id"],
            2 * limit,
            api="history"
        )
        trades = []
        for f in filled:
            data = {}
            if f["op"]["account_id"] == account["id"]:
                data["date"] = formatTimeString(f["time"])
                data["price"] = Price(f, base=self["base"], quote=self["quote"])
                if f["op"]["pays"]["asset_id"] == m["base"]:
                    data["type"] = "buy"
                    data["amount"] = int(f["op"]["receives"]["amount"]) / 10 ** quote["precision"]
                else:
                    data["type"] = "sell"
                    data["amount"] = int(f["op"]["pays"]["amount"]) / 10 ** quote["precision"]
                data["total"] = data["amount"] * data["rate"]
                trades.append(data)
        return trades
        """

    def buy(self,
            price,
            amount,
            expiration=7 * 24 * 60 * 60,
            killfill=False,
            account=None
            ):
        """ Places a buy order in a given market 

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to buy
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        if isinstance(price, Price):
            assert (
                price["quote"]["symbol"] == self["quote"]["symbol"] and 
                price["base"]["symbol"] == self["base"]["symbol"]
            )
        if isinstance(amount, Amount):
            assert(amount["asset"]["symbol"] == self["quote"]["symbol"])

        account = Account(account, bitshares_instance=self.bitshares)
        order = operations.Limit_order_create(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "seller": account["id"],
            "amount_to_sell": {
                "amount": int(float(amount) * float(price) * 10 ** self["base"]["precision"]),
                "asset_id": self["base"]["id"]
            },
            "min_to_receive": {
                "amount": int(float(amount) * 10 ** self["quote"]["precision"]),
                "asset_id": self["quote"]["id"]
            },
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
        })
        return self.bitshares.finalizeOp(order, account["name"], "active")

    def sell(self,
            price,
            amount,
            expiration=7 * 24 * 60 * 60,
            killfill=False,
            account=None
            ):
        """ Places a sell order in a given market 

            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to sell
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param string account: Account name that executes that order

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reversed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if not account:
            if "default_account" in self.bitshares.config:
                account = self.bitshares.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, bitshares_instance=self.bitshares)
        if isinstance(price, Price):
            assert (
                price["quote"]["symbol"] == self["quote"]["symbol"] and 
                price["base"]["symbol"] == self["base"]["symbol"]
            )
        if isinstance(amount, Amount):
            assert(amount["asset"]["symbol"] == self["quote"]["symbol"])
        order = operations.Limit_order_create(**{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "seller": account["id"],
            "amount_to_sell": {
                "amount": int(float(amount) * 10 ** self["quote"]["precision"]),
                "asset_id": self["quote"]["id"]
            },
            "min_to_receive": {
                "amount": int(float(amount) * float(price) * 10 ** self["base"]["precision"]),
                "asset_id": self["base"]["id"]
            },
            "expiration": formatTimeFromNow(expiration),
            "fill_or_kill": killfill,
        })
        return self.bitshares.finalizeOp(order, account["name"], "active")
