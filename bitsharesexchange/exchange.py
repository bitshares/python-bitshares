from bitsharesdeprecated.client import BitSharesClient
from bitsharesbase import transactions
from bitsharesbase.operations import operations
from bitsharesbase.account import PrivateKey, PublicKey
from bitsharesbase import memo as Memo
from datetime import datetime
import time
import math
from .proposal import Proposal
import logging
from . import deep_eq
log = logging.getLogger(__name__)


class NoWalletException(Exception):
    pass


class InvalidWifKey(Exception):
    pass


class WifNotActive(Exception):
    pass


class ExampleConfig():
    """ The behavior of your program can be
        defined in a separated class (here called ``ExampleConfig()``. It
        contains the wallet and witness connection parameters:

        Configuration Rules:

        * `witness_url` is required in all cases
        * If you want to run a bot continuously, the configuration needs
          to be inherited from `BitSharesWebsocketProtocol`
        * Either you provide access to a cli_wallet via `wallet_host`
          (etc.) or your need to provide the **active private key** to the
          account as `wif`

        The config class is used to define several attributes *and*
        methods that will be used during API communication..

        .. code-block:: python

            class Config(BitSharesWebsocketProtocol):  # Note the dependency
                wallet_host = "localhost"
                wallet_port = 8092
                wallet_user = ""
                wallet_password = ""
                witness_url = "ws://localhost:8090/"
                witness_user = ""
                witness_password = ""
                wif = None

        All methods within ``bitshares.rpc`` are mapped to the
        corresponding RPC call of the **wallet** and the parameters are
        handed over directly. Similar behavior is implemented for
        ``bitshares.ws`` which can deal with calls to the **witness
        node**.

        This allows the use of rpc commands similar to the
        ``BitSharesAPI`` class:

        .. code-block:: python

            bitshares = BitSharesExchange(Config)
            # Calls to the cli-wallet
            print(bitshares.rpc.info())
            # Calls to the witness node
            print(bitshares.ws.get_account("init0"))
            print(bitshares.ws.get_asset("USD"))
            print(bitshares.ws.get_account_count())

    """

    #: Wallet connection parameters
    wallet_host = "localhost"
    wallet_port = 8092
    wallet_user = ""
    wallet_password = ""

    #: Witness connection parameter
    witness_url = "ws://localhost:8090/"
    witness_user = ""
    witness_password = ""

    #: The account used here
    account = "fabian"
    wif = None

    #: Markets to watch.
    watch_markets = ["USD_BTS"]
    market_separator = "_"


class BitSharesExchange(BitSharesClient):
    """ This class serves as an abstraction layer for the decentralized
        exchange within the network and simplifies interaction for
        trading bots.

        :param config config: Configuration Class, similar to the
                              example above

        This class tries to map the poloniex API around the DEX but has
        some differences:

            * market pairs are denoted as 'quote'_'base', e.g. `USD_BTS`
            * Prices/Rates are denoted in 'base', i.e. the USD_BTS market
              is priced in BTS per USD.
              Example: in the USD_BTS market, a price of 300 means
              a USD is worth 300 BTS
            * All markets could be considered reversed as well ('BTS_USD')

        Usage:

        .. code-block:: python


            from BitSharesExchange import BitSharesExchange
            import json


            class Config():
                wallet_host = "localhost"
                wallet_port = 8092
                wallet_user = ""
                wallet_password = ""
                witness_url = "ws://10.0.0.16:8090/"
                witness_user = ""
                witness_password = ""

                watch_markets = ["USD_BTS", "GOLD_BTS"]
                market_separator = "_"
                account = "fabian"
                wif = None

            if __name__ == '__main__':
                dex = BitSharesExchange(Config)
                print(json.dumps(dex.returnTradeHistory("USD_BTS"),indent=4))
                print(json.dumps(dex.returnTicker(),indent=4))
                print(json.dumps(dex.return24Volume(),indent=4))
                print(json.dumps(dex.returnOrderBook("USD_BTS"),indent=4))
                print(json.dumps(dex.returnBalances(),indent=4))
                print(json.dumps(dex.returnOpenOrders("all"),indent=4))
                print(json.dumps(dex.buy("USD_BTS", 0.001, 10),indent=4))
                print(json.dumps(dex.sell("USD_BTS", 0.001, 10),indent=4))
    """
    markets = {}

    #: store assets as static variable to speed things up!
    assets = {}

    #: The trading account
    myAccount = None

    def __init__(self, config, **kwargs):
        # Defaults:
        self.safe_mode = True

        #: Propose transactions (instead of broadcasting every order, we
        #  here propose every order in a single proposal
        self.propose_only = False
        self.propose_operations = []

        if "safe_mode" in kwargs:
            self.safe_mode = kwargs["safe_mode"]
        if "propose_only" in kwargs:
            self.propose_only = kwargs["propose_only"]

        if "prefix" in kwargs:
            self.prefix = kwargs["prefix"]
        else:
            self.prefix = getattr(config, "prefix", "BTS")

        #: The wif key can be used for creating transactions **if** not
        # connected to a cli_wallet
        if not hasattr(config, "wif"):
            setattr(config, "wif", None)
        if not getattr(config, "wif"):
            config.wif = None
        else:
            # Test for valid Private Key
            try:
                config.wif = str(PrivateKey(config.wif))
            except:
                raise InvalidWifKey

        if not hasattr(config, "memo_wif"):
            setattr(config, "memo_wif", None)
        if not getattr(config, "memo_wif"):
            config.memo_wif = None
        else:
            # Test for valid Private Key
            try:
                config.memo_wif = str(PrivateKey(config.memo_wif))
            except:
                raise InvalidWifKey

        self.config = config
        super().__init__(config)

        # Get my Account
        self.myAccount = self.getMyAccount()

        if not self.myAccount:
            raise ValueError(
                "Couldn't find account name %s" % self.config.account +
                " on the chain! Please double-check!"
            )

        # Now verify that the given wif key has active permissions:
        if getattr(config, "wif") and config.wif:
            pubkey = format(PrivateKey(config.wif).pubkey, self.prefix)
            if not any(filter(
                lambda x: x[0] == pubkey, self.myAccount["active"]["key_auths"]
            )):
                raise WifNotActive

    def executeOps(self, ops):
        expiration = transactions.formatTimeFromNow(30)
        ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
        ref_block_num, ref_block_prefix = transactions.getBlockParams(self.ws)
        transaction = transactions.Signed_Transaction(
            ref_block_num=ref_block_num,
            ref_block_prefix=ref_block_prefix,
            expiration=expiration,
            operations=ops
        )
        transaction = transaction.sign([self.config.wif], self.prefix)
        transaction = transaction.json()
        if not (self.safe_mode or self.propose_only):
            self.ws.broadcast_transaction(transaction, api="network_broadcast")
        return transaction

    def formatTimeFromNow(self, secs=0):
        """ Properly Format Time that is `x` seconds in the future

            :param int secs: Seconds to go in the future (`x>0`) or the
                             past (`x<0`)
            :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
            :rtype: str

        """
        return datetime.utcfromtimestamp(time.time() + int(secs)).strftime('%Y-%m-%dT%H:%M:%S')

    def normalizePrice(self, market, price):
        """ Because assets have different precisions and orders are
            created with a rational price, prices defined in floats will
            slightly differ from the actual prices on the blockchain.
            This is a representation issuer between floats being
            represented as a ratio of integer (satoshis)
        """
        m = self._get_assets_from_market(market)
        base = m["base"]
        quote = m["quote"]
        return float(
            (int(price * 10 ** (base["precision"] - quote["precision"])) /
             10 ** (base["precision"] - quote["precision"])))

    def _get_market_name_from_ids(self, quote_id, base_id):
        """ Returns the properly formated name of a market given base
            and quote ids

            :param str quote_id: Object ID of the quote asset
            :param str base_id: Object ID of the base asset
            :return: Market name with proper separator
            :rtype: str
        """
        quote = self._get_asset(quote_id)
        base = self._get_asset(base_id)
        return quote["symbol"] + self.market_separator + base["symbol"]

    def getMyAccount(self):
        return self.ws.get_account(self.config.account)

    def _get_asset(self, i):
        if i in self.assets:
            return self.assets[i]
        else:
            asset = self.ws.get_asset(i)
            self.assets[asset["id"]] = asset
            self.assets[asset["symbol"]] = asset
            return asset

    def _get_assets_from_ids(self, base_id, quote_id):
        """ Returns assets of a market given base
            and quote ids

            :param str quote_id: Object ID of the quote asset
            :param str base_id: Object ID of the base asset
            :return: object that contains `quote` and `base` asset objects
            :rtype: json
        """
        quote = self._get_asset(quote_id)
        base = self._get_asset(base_id)
        return {"quote": quote, "base": base}

    def _get_asset_ids_from_name(self, market):
        """ Returns the  base and quote ids given a properly formated
            market name

            :param str market: Market name (properly separated)
            :return: object that contains `quote` asset id and `base` asset id
            :rtype: json
        """
        quote_symbol, base_symbol = market.split(self.market_separator)
        quote = self._get_asset(quote_symbol)
        base = self._get_asset(quote_symbol)
        return {"quote": quote["id"], "base": base["id"]}

    def _get_assets_from_market(self, market):
        """ Returns the  base and quote assets given a properly formated
            market name

            :param str market: Market name (properly separated)
            :return: object that contains `quote` and `base` asset objects
            :rtype: json
        """
        quote_symbol, base_symbol = market.split(self.market_separator)
        quote = self._get_asset(quote_symbol)
        base = self._get_asset(base_symbol)
        return {"quote": quote, "base": base}

    def _get_price(self, o):
        """ Given an object with `quote` and `base`, derive the correct
            price.

            :param Object o: Blockchain object that contains `quote` and `asset` amounts and asset ids.
            :return: price derived as `base`/`quote`

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        quote_amount = float(o["quote"]["amount"])
        base_amount = float(o["base"]["amount"])
        quote_id = o["quote"]["asset_id"]
        base_id = o["base"]["asset_id"]
        base = self._get_asset(base_id)
        quote = self._get_asset(quote_id)
        # invert price!
        if (quote_amount / 10 ** quote["precision"]) > 0.0:
            return float((base_amount / 10 ** base["precision"]) /
                         (quote_amount / 10 ** quote["precision"]))
        else:
            return None

    def _get_price_filled(self, f, m):
        """ A filled order has `receives` and `pays` ops which serve as
            `base` and `quote` depending on sell or buy

            :param Object f: Blockchain object for filled orders
            :param str m: Market
            :return: Price

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.
            Example: in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.

        """
        r = {}
        if f["op"]["receives"]["asset_id"] == m["base"]:
            # If the seller received "base" in a quote_base market, than
            # it has been a sell order of quote
            r["base"] = f["op"]["receives"]
            r["quote"] = f["op"]["pays"]
        else:
            # buy order
            r["base"] = f["op"]["pays"]
            r["quote"] = f["op"]["receives"]
        # invert price!
        return self._get_price(r)

    def _get_txorder_price(self, f, m):
        """ A newly place limit order has `amount_to_sell` and
            `min_to_receive` which serve as `base` and `quote` depending
            on sell or buy

            :param Object f: Blockchain object for historical orders
            :param str m: Market
            :return: Price
        """
        r = {}
        if f["min_to_receive"]["asset_id"] == m["base"]:
            # If the seller received "base" in a quote_base market, than
            # it has been a sell order of quote
            r["base"] = f["min_to_receive"]
            r["quote"] = f["amount_to_sell"]
        elif f["min_to_receive"]["asset_id"] == m["quote"]:
            # buy order
            r["base"] = f["amount_to_sell"]
            r["quote"] = f["min_to_receive"]
        else:
            return None
        # invert price!
        return self._get_price(r)

    def returnCurrencies(self):
        """ In contrast to poloniex, this call returns the assets of the
            watched markets only.

            Example Output:

            .. code-block:: js

                {'BTS': {'issuer': '1.2.3', 'id': '1.3.0', 'dynamic_asset_data_id': '2.3.0', 'precision': 5, 'symbol': 'BTS', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.0', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 1}}, 'flags': 0, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 0, 'max_supply': '360057050210207'}}, 'GOLD': {'issuer': '1.2.0', 'id': '1.3.106', 'dynamic_asset_data_id': '2.3.106', 'precision': 6, 'bitasset_data_id': '2.4.6', 'symbol': 'GOLD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 troy ounce .999 fine gold', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.106', 'amount': 1}, 'quote': {'asset_id': '1.3.0', 'amount': 34145}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}, 'USD': {'issuer': '1.2.0', 'id': '1.3.121', 'dynamic_asset_data_id': '2.3.121', 'precision': 4, 'bitasset_data_id': '2.4.21', 'symbol': 'USD', 'options': {'max_market_fee': '1000000000000000', 'blacklist_authorities': [], 'blacklist_markets': [], 'description': '1 United States dollar', 'whitelist_authorities': [], 'market_fee_percent': 0, 'core_exchange_rate': {'base': {'asset_id': '1.3.121', 'amount': 5}, 'quote': {'asset_id': '1.3.0', 'amount': 15751}}, 'flags': 128, 'extensions': [], 'whitelist_markets': [], 'issuer_permissions': 511, 'max_supply': '1000000000000000'}}}

        """
        r = {}
        asset_ids = []
        for market in self.markets:
            m = self.markets[market]
            asset_ids.append(m["base"])
            asset_ids.append(m["quote"])
        asset_ids_unique = list(set(asset_ids))
        assets = self.ws.get_objects(asset_ids_unique)
        for a in assets:
            r.update({a["symbol"]: a})
        return r

    def returnFees(self):
        """ Returns a dictionary of all fees that apply through the
            network

            Example output:

            .. code-block:: js

                {'proposal_create': {'fee': 400000.0},
                'asset_publish_feed': {'fee': 1000.0}, 'account_create':
                {'basic_fee': 950000.0, 'price_per_kbyte': 20000.0,
                'premium_fee': 40000000.0}, 'custom': {'fee': 20000.0},
                'asset_fund_fee_pool': {'fee': 20000.0},
                'override_transfer': {'fee': 400000.0}, 'fill_order':
                {}, 'asset_update': {'price_per_kbyte': 20000.0, 'fee':
                200000.0}, 'asset_update_feed_producers': {'fee':
                10000000.0}, 'assert': {'fee': 20000.0},
                'committee_member_create': {'fee': 100000000.0}}

        """
        r = {}
        obj, base = self.ws.get_objects(["2.0.0", "1.3.0"])
        fees = obj["parameters"]["current_fees"]["parameters"]
        scale = float(obj["parameters"]["current_fees"]["scale"])
        for f in fees:
            op_name = "unknown %d" % f[0]
            for name in operations:
                if operations[name] == f[0]:
                    op_name = name
            fs = f[1]
            for _type in fs:
                fs[_type] = float(fs[_type]) * scale / 1e4 / 10 ** base["precision"]
            r[op_name] = fs
        return r

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
                    "BTS_USD": {
                        "quoteVolume": 144.1862,
                        "settlement_price": 0.003009016674102742,
                        "lowestAsk": 0.002992220227408737,
                        "baseVolume": 48328.73333,
                        "percentChange": 2.0000000097901705,
                        "highestBid": 0.0029411764705882353,
                        "last": 0.003000000000287946,
                        "core_exchange_rate": 0.003161120960980772
                    },
                    "USD_BTS": {
                        "quoteVolume": 48328.73333,
                        "settlement_price": 332.3344827586207,
                        "lowestAsk": 340.0,
                        "baseVolume": 144.1862,
                        "percentChange": -1.9607843231354893,
                        "highestBid": 334.20000000000005,
                        "last": 333.33333330133934,
                        "core_exchange_rate": 316.3434782608696
                    }
                }

            .. note:: A market that has had no trades will result in
                      prices of "-1" to indicate that no trades have
                      happend.

        """
        r = {}
        for market in self.markets:
            m = self.markets[market]
            data = {}
            quote_asset = self._get_asset(m["quote"])
            base_asset = self._get_asset(m["base"])
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 1, api="history")
            # Price and ask/bids
            if filled:
                data["last"] = self._get_price_filled(filled[0], m)
            else:
                data["last"] = -1

            orders = self.ws.get_limit_orders(
                m["quote"], m["base"], 1)
            if len(orders) > 1:
                data["lowestAsk"] = (1 / self._get_price(orders[0]["sell_price"]))
                data["highestBid"] = self._get_price(orders[1]["sell_price"])
            else:
                data["lowestAsk"] = -1
                data["highestBid"] = -1

            # Core Exchange rate
            if quote_asset["id"] != "1.3.0":
                data["core_exchange_rate"] = 1.0 / self._get_price(quote_asset["options"]["core_exchange_rate"])
            else:
                data["core_exchange_rate"] = self._get_price(base_asset["options"]["core_exchange_rate"])

            # smartcoin stuff
            if "bitasset_data_id" in quote_asset:
                bitasset = self.getObject(quote_asset["bitasset_data_id"])
                backing_asset_id = bitasset["options"]["short_backing_asset"]
                if backing_asset_id == base_asset["id"]:
                    data["settlement_price"] = 1 / self._get_price(bitasset["current_feed"]["settlement_price"])
            elif "bitasset_data_id" in base_asset:
                bitasset = self.getObject(base_asset["bitasset_data_id"])
                backing_asset_id = bitasset["options"]["short_backing_asset"]
                if backing_asset_id == quote_asset["id"]:
                    data["settlement_price"] = self._get_price(bitasset["current_feed"]["settlement_price"])

            if len(marketHistory):
                if marketHistory[0]["key"]["quote"] == m["quote"]:
                    data["baseVolume"] = float(marketHistory[0]["base_volume"]) / (10 ** base_asset["precision"])
                    data["quoteVolume"] = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_base"]) / 10 ** base_asset["precision"]) /
                                (float(marketHistory[0]["open_quote"]) / 10 ** quote_asset["precision"]))
                else:
                    #: Looks weird but is correct:
                    data["baseVolume"] = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data["quoteVolume"] = float(marketHistory[0]["base_volume"]) / (10 ** quote_asset["precision"])
                    price24h = ((float(marketHistory[0]["open_quote"]) / 10 ** base_asset["precision"]) /
                                (float(marketHistory[0]["open_base"]) / 10 ** quote_asset["precision"]))
                data["price24h"] = price24h
                data["percentChange"] = ((data["last"] / price24h - 1) * 100)
            else:
                data["baseVolume"] = 0
                data["quoteVolume"] = 0
                data["percentChange"] = 0
            r.update({market: data})
        return r

    def return24Volume(self):
        """ Returns the 24-hour volume for all markets, plus totals for primary currencies.

            Sample output:

            .. code-block:: js

                {
                    "USD_BTS": {
                        "BTS": 361666.63617,
                        "USD": 1087.0
                    },
                    "GOLD_BTS": {
                        "BTS": 0,
                        "GOLD": 0
                    }
                }

        """
        r = {}
        for market in self.markets:
            m = self.markets[market]
            marketHistory = self.ws.get_market_history(
                m["quote"], m["base"],
                24 * 60 * 60,
                self.formatTimeFromNow(-24 * 60 * 60),
                self.formatTimeFromNow(),
                api="history")
            quote_asset = self._get_asset(m["quote"])
            base_asset = self._get_asset(m["base"])
            data = {}
            if len(marketHistory):
                if marketHistory[0]["key"]["quote"] == m["quote"]:
                    data[m["base_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** quote_asset["precision"])
                else:
                    data[m["base_symbol"]] = float(marketHistory[0]["quote_volume"]) / (10 ** base_asset["precision"])
                    data[m["quote_symbol"]] = float(marketHistory[0]["base_volume"]) / (10 ** quote_asset["precision"])
            else:
                data[m["base_symbol"]] = 0
                data[m["quote_symbol"]] = 0
            r.update({market: data})
        return r

    def returnOrderBook(self, currencyPair="all", limit=25):
        """ Returns the order book for a given market. You may also
            specify "all" to get the orderbooks of all markets.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param int limit: Limit the amount of orders (default: 25)

            Ouput is formated as:::

                [price, amount, orderid]

            * price is denoted in base per quote
            * amount is in quote

            Sample output:

            .. code-block:: js

                {'USD_BTS': {'asks': [[0.0003787878787878788, 203.1935],
                [0.0003799587270281197, 123.65374999999999]], 'bids':
                [[0.0003676470588235294, 9.9], [0.00036231884057971015,
                10.0]]}, 'GOLD_BTS': {'asks': [[2.25e-05,
                0.045000000000000005], [2.3408239700374533e-05,
                0.33333333333333337]], 'bids': [[2.0833333333333333e-05,
                0.4], [1.851851851851852e-05, 0.0001]]}}

            .. note:: A maximum of 25 orders will be returned!

        """
        r = {}
        if currencyPair == "all":
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets:
            m = self.markets[market]
            orders = self.ws.get_limit_orders(
                m["quote"], m["base"], limit)
            quote_asset = self._get_asset(m["quote"])
            base_asset = self._get_asset(m["base"])
            asks = []
            bids = []
            for o in orders:
                if o["sell_price"]["base"]["asset_id"] == m["base"]:
                    price = self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** base_asset["precision"] / self._get_price(o["sell_price"])
                    bids.append([price, volume, o["id"]])
                else:
                    price = 1 / self._get_price(o["sell_price"])
                    volume = float(o["for_sale"]) / 10 ** quote_asset["precision"]
                    asks.append([price, volume, o["id"]])

            data = {"asks": asks, "bids": bids}
            r.update({market: data})
        return r

    def returnBalances(self):
        """ Returns all of your balances.

            Example Output:

            .. code-block:: js

                {
                    "BROWNIE.PTS": 2499.9999,
                    "EUR": 0.0028,
                    "BTS": 1893552.94893,
                    "OPENBTC": 0.00110581,
                    "GREENPOINT": 0.0
                }

        """
        balances = self.ws.get_account_balances(self.myAccount["id"], [])
        asset_ids = [a["asset_id"] for a in balances]
        assets = self.ws.get_objects(asset_ids)
        data = {}
        for i, asset in enumerate(assets):
            amount = float(balances[i]["amount"]) / 10 ** asset["precision"]
            if amount == 0.0:
                continue
            data[asset["symbol"]] = amount
        return data

    def returnOpenOrdersIds(self, currencyPair="all"):
        """ Returns only the ids of open Orders
        """
        r = {}
        if currencyPair == "all":
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        orders = self.ws.get_full_accounts([self.myAccount["id"]], False)[0][1]["limit_orders"]
        for market in markets:
            r[market] = []
        for o in orders:
            for market in markets:
                m = self.markets[market]
                if ((o["sell_price"]["base"]["asset_id"] == m["base"] and
                    o["sell_price"]["quote"]["asset_id"] == m["quote"]) or
                    (o["sell_price"]["base"]["asset_id"] == m["quote"] and
                        o["sell_price"]["quote"]["asset_id"] ==
                        m["base"])):
                    r[market].append(o["id"])
        return r

    def returnOpenOrders(self, currencyPair="all"):
        """ Returns your open orders for a given market, specified by
            the "currencyPair.

            :param str currencyPair: Return results for a particular market only (default: "all")

            Output Parameters:

                - `type`: sell or buy order for `quote`
                - `rate`: price for `base` per `quote`
                - `orderNumber`: identifier (e.g. for cancelation)
                - `amount`: amount of quote
                - `total`: amount of base at asked price (amount/price)
                - `amount_to_sell`: "amount_to_sell"

            .. note:: Ths method will not show orders of markets that
                      are **not** in the ``watch_markets`` array!

            Example:

            .. code-block:: js

                {
                    "USD_BTS": [
                        {
                            "orderNumber": "1.7.1505",
                            "type": "buy",
                            "rate": 341.74559999999997,
                            "total": 341.74559999999997,
                            "amount": 1.0
                        },
                        {
                            "orderNumber": "1.7.1512",
                            "type": "buy",
                            "rate": 325.904045,
                            "total": 325.904045,
                            "amount": 1.0
                        },
                        {
                            "orderNumber": "1.7.1513",
                            "type": "sell",
                            "rate": 319.45050000000003,
                            "total": 31945.05,
                            "amount": 1020486.2195025001
                        }
                    ]
                }

        """
        r = {}
        if currencyPair == "all":
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        orders = self.ws.get_full_accounts([self.myAccount["id"]], False)[0][1]["limit_orders"]
        for market in markets:
            r[market] = []
        for o in orders:
            base_id = o["sell_price"]["base"]["asset_id"]
            base_asset = self._get_asset(base_id)
            for market in markets:
                m = self.markets[market]
                if (o["sell_price"]["base"]["asset_id"] == m["base"] and
                        o["sell_price"]["quote"]["asset_id"] == m["quote"]):
                    # buy
                    amount = float(o["for_sale"]) / 10 ** base_asset["precision"] / self._get_price(o["sell_price"])
                    rate = self._get_price(o["sell_price"])
                    t = "buy"
                    total = amount * rate
                    for_sale = float(o["for_sale"]) / 10 ** base_asset["precision"]
                elif (o["sell_price"]["base"]["asset_id"] == m["quote"] and
                        o["sell_price"]["quote"]["asset_id"] == m["base"]):
                    # sell
                    amount = float(o["for_sale"]) / 10 ** base_asset["precision"]
                    rate = 1 / self._get_price(o["sell_price"])
                    t = "sell"
                    total = amount * rate
                    for_sale = float(o["for_sale"]) / 10 ** base_asset["precision"]
                else:
                    continue
                r[market].append({"rate": rate,
                                  "amount": amount,
                                  "total": total,
                                  "type": t,
                                  "amount_to_sell": for_sale,
                                  "orderNumber": o["id"]})
        return r

    def returnOpenOrdersStruct(self, currencyPair="all"):
        """ This method is similar to ``returnOpenOrders`` but has a different
            output format:

            Example:

            .. code-block:: js

                {
                    "USD_BTS": {
                       "1.7.1505": {
                            "orderNumber": "1.7.1505",
                            "type": "buy",
                            "rate": 341.74559999999997,
                            "total": 341.74559999999997,
                            "amount": 1.0
                        },
                        "1.7.1512": {
                            "orderNumber": "1.7.1512",
                            "type": "buy",
                            "rate": 325.904045,
                            "total": 325.904045,
                            "amount": 1.0
                        },
                        "1.7.1513": {
                            "orderNumber": "1.7.1513",
                            "type": "sell",
                            "rate": 319.45050000000003,
                            "total": 31945.05,
                            "amount": 1020486.2195025001
                        }
                    ]
                }
        """
        orders = self.returnOpenOrders(currencyPair)
        r = {}
        for market in orders:
            r[market] = {}
            for order in orders[market]:
                r[market][order["orderNumber"]] = order
        return r

    def returnTradeHistory(self, currencyPair="all", limit=25):
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
        r = {}
        if currencyPair == "all":
            markets = list(self.markets.keys())
        else:
            markets = [currencyPair]
        for market in markets:
            m = self.markets[market]
            filled = self.ws.get_fill_order_history(
                m["quote"], m["base"], 2 * limit, api="history")
            trades = []
            for f in filled:
                data = {}
                data["date"] = f["time"]
                data["rate"] = self._get_price_filled(f, m)
                quote = self._get_asset(m["quote"])
                if f["op"]["account_id"] == self.myAccount["id"]:
                    if f["op"]["pays"]["asset_id"] == m["base"]:
                        data["type"] = "buy"
                        data["amount"] = int(f["op"]["receives"]["amount"]) / 10 ** quote["precision"]
                    else:
                        data["type"] = "sell"
                        data["amount"] = int(f["op"]["pays"]["amount"]) / 10 ** quote["precision"]
                    data["total"] = data["amount"] * data["rate"]
                    trades.append(data)
            r.update({market: trades})
        return r

    def buy(self,
            currencyPair,
            rate,
            amount,
            expiration=7 * 24 * 60 * 60,
            killfill=False,
            returnID=False):
        """ Places a buy order in a given market (buy ``quote``, sell
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to buy
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param bool returnID: If this flag is True, the call will wait for the order to be included in a block and return it's id

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        # We buy quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        base = self._get_asset(base_symbol)
        quote = self._get_asset(quote_symbol)
        if self.rpc:
            transaction = self.rpc.sell_asset(self.config.account,
                                              '{:.{prec}f}'.format(amount * rate, prec=base["precision"]),
                                              base_symbol,
                                              '{:.{prec}f}'.format(amount, prec=quote["precision"]),
                                              quote_symbol,
                                              expiration,
                                              killfill,
                                              not (self.safe_mode or self.propose_only))
            jsonOrder = transaction["operations"][0][1]
        elif self.config.wif:
            s = {"fee": {"amount": 0, "asset_id": "1.3.0"},
                 "seller": self.myAccount["id"],
                 "amount_to_sell": {"amount": int(amount * rate * 10 ** base["precision"]),
                                    "asset_id": base["id"]
                                    },
                 "min_to_receive": {"amount": int(amount * 10 ** quote["precision"]),
                                    "asset_id": quote["id"]
                                    },
                 "expiration": transactions.formatTimeFromNow(expiration),
                 "fill_or_kill": killfill,
                 }
            order = transactions.Limit_order_create(**s)
            ops = [transactions.Operation(order)]
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if returnID:
            return self._waitForOperationsConfirmation(jsonOrder)
        else:
            if self.propose_only:
                [self.propose_operations.append(o) for o in transaction["operations"]]
                return self.propose_operations
            else:
                return transaction

    def sell(self,
             currencyPair,
             rate,
             amount,
             expiration=7 * 24 * 60 * 60,
             killfill=False,
             returnID=False):
        """ Places a sell order in a given market (sell ``quote``, buy
            ``base`` in market ``quote_base``). Required POST parameters
            are "currencyPair", "rate", and "amount". If successful, the
            method will return the order creating (signed) transaction.

            :param str currencyPair: Return results for a particular market only (default: "all")
            :param float price: price denoted in ``base``/``quote``
            :param number amount: Amount of ``quote`` to sell
            :param number expiration: (optional) expiration time of the order in seconds (defaults to 7 days)
            :param bool killfill: flag that indicates if the order shall be killed if it is not filled (defaults to False)
            :param bool returnID: If this flag is True, the call will wait for the order to be included in a block and return it's id

            Prices/Rates are denoted in 'base', i.e. the USD_BTS market
            is priced in BTS per USD.

            **Example:** in the USD_BTS market, a price of 300 means
            a USD is worth 300 BTS

            .. note::

                All prices returned are in the **reveresed** orientation as the
                market. I.e. in the BTC/BTS market, prices are BTS per BTC.
                That way you can multiply prices with `1.05` to get a +5%.
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        # We sell quote and pay with base
        quote_symbol, base_symbol = currencyPair.split(self.market_separator)
        base = self._get_asset(base_symbol)
        quote = self._get_asset(quote_symbol)
        if self.rpc:
            transaction = self.rpc.sell_asset(self.config.account,
                                              '{:.{prec}f}'.format(amount, prec=quote["precision"]),
                                              quote_symbol,
                                              '{:.{prec}f}'.format(amount * rate, prec=base["precision"]),
                                              base_symbol,
                                              expiration,
                                              killfill,
                                              not (self.safe_mode or self.propose_only))
            jsonOrder = transaction["operations"][0][1]
        elif self.config.wif:
            s = {"fee": {"amount": 0, "asset_id": "1.3.0"},
                 "seller": self.myAccount["id"],
                 "amount_to_sell": {"amount": int(amount * 10 ** quote["precision"]),
                                    "asset_id": quote["id"]
                                    },
                 "min_to_receive": {"amount": int(amount * rate * 10 ** base["precision"]),
                                    "asset_id": base["id"]
                                    },
                 "expiration": transactions.formatTimeFromNow(expiration),
                 "fill_or_kill": killfill,
                 }
            order = transactions.Limit_order_create(**s)
            ops = [transactions.Operation(order)]
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if returnID:
            return self._waitForOperationsConfirmation(jsonOrder)
        else:
            if self.propose_only:
                [self.propose_operations.append(o) for o in transaction["operations"]]
                return self.propose_operations
            else:
                return transaction

    def _waitForOperationsConfirmation(self, thisop):
        if self.safe_mode:
            return "Safe Mode enabled, can't obtain an orderid"

        log.debug("Waiting for operation to be included in block: %s" % str(thisop))
        counter = -2
        blocknum = int(self.ws.get_dynamic_global_properties()["head_block_number"])
        for block in self.ws.block_stream(start=blocknum - 2, mode="head"):
            counter += 1
            for tx in block["transactions"]:
                for i, op in enumerate(tx["operations"]):
                    if deep_eq.deep_eq(op[1], thisop):
                        return (tx["operation_results"][i][1])
            if counter > 10:
                raise Exception("The operation has not been added after 10 blocks!")

    def list_debt_positions(self):
        """ List Call Positions (borrowed assets and amounts)

            :return: Struct of assets with amounts and call price
            :rtype: json

            **Example**:

            .. code-block: js

                {'USD': {'collateral': '865893.75000',
                         'collateral_asset': 'BTS',
                         'debt': 120.00000}

        """
        debts = self.ws.get_full_accounts([self.myAccount["id"]], False)[0][1]["call_orders"]
        r = {}
        for debt in debts:
            base = self.getObject(debt["call_price"]["base"]["asset_id"])
            quote = self.getObject(debt["call_price"]["quote"]["asset_id"])

            if "bitasset_data_id" not in quote:
                continue

            bitasset = self.getObject(quote["bitasset_data_id"])
            settlement_price = self._get_price(bitasset["current_feed"]["settlement_price"])

            if not settlement_price:
                continue

            call_price = self._get_price(debt["call_price"])
            collateral_amount = int(debt["collateral"]) / 10 ** base["precision"]
            debt_amount = int(debt["debt"]) / 10 ** quote["precision"]

            r[quote["symbol"]] = {"collateral_asset": base["symbol"],
                                  "collateral": collateral_amount,
                                  "debt": debt_amount,
                                  "call_price": call_price,
                                  "settlement_price": settlement_price,
                                  "ratio": collateral_amount / debt_amount * settlement_price}
        return r

    def close_debt_position(self, symbol):
        """ Close a debt position and reclaim the collateral

            :param str symbol: Symbol to close debt position for
            :raises ValueError: if symbol has no open call position
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        debts = self.list_debt_positions()
        if symbol not in debts:
            raise ValueError("No call position open for %s" % symbol)
        debt = debts[symbol]
        asset = self._get_asset(symbol)
        collateral_asset = self._get_asset(debt["collateral_asset"])

        if self.rpc:
            transaction = self.rpc.borrow_asset(self.config.account,
                                                '{:.{prec}f}'.format(-debt["debt"], prec=asset["precision"]),
                                                symbol,
                                                '{:.{prec}f}'.format(-debt["collateral"], prec=collateral_asset["precision"]),
                                                not (self.safe_mode or self.propose_only))
        elif self.config.wif:
            s = {'fee': {'amount': 0, 'asset_id': '1.3.0'},
                 'delta_debt': {'amount': int(-debt["debt"] * 10 ** asset["precision"]),
                                'asset_id': asset["id"]},
                 'delta_collateral': {'amount': int(-debt["collateral"] * 10 ** collateral_asset["precision"]),
                                      'asset_id': collateral_asset["id"]},
                 'funding_account': self.myAccount["id"],
                 'extensions': []}
            ops = [transactions.Operation(transactions.Call_order_update(**s))]
            ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction

    def adjust_debt(self, delta_debt, symbol, new_collateral_ratio=None):
        """ Adjust the amount of debt for an asset

            :param float delta_debt: Delta of the debt (-10 means reduce debt by 10, +10 means borrow another 10)
            :param str symbol: Asset to borrow
            :param float new_collateral_ratio: collateral ratio to maintain (optional, by default tries to maintain old ratio)
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        # We sell quote and pay with base
        asset = self._get_asset(symbol)
        if "bitasset_data_id" not in asset:
            raise ValueError("%s is not a bitasset!" % symbol)
        bitasset = self.getObject(asset["bitasset_data_id"])

        # Check minimum collateral ratio
        backing_asset_id = bitasset["options"]["short_backing_asset"]
        maintenance_col_ratio = bitasset["current_feed"]["maintenance_collateral_ratio"] / 1000
        if maintenance_col_ratio > new_collateral_ratio:
            raise ValueError("Collateral Ratio has to be higher than %5.2f" % maintenance_col_ratio)

        # Derive Amount of Collateral
        collateral_asset = self._get_asset(backing_asset_id)
        settlement_price = self._get_price(bitasset["current_feed"]["settlement_price"])

        current_debts = self.list_debt_positions()
        if symbol not in current_debts:
            raise ValueError("No Call position available to adjust! Please borrow first!")

        amount_of_collateral = (current_debts[symbol]["debt"] + delta_debt) * new_collateral_ratio / settlement_price
        amount_of_collateral -= current_debts[symbol]["collateral"]

        # Verify that enough funds are available
        balances = self.returnBalances()
        fundsNeeded = amount_of_collateral + self.returnFees()["call_order_update"]["fee"]
        fundsHave = balances[collateral_asset["symbol"]]
        if fundsHave <= fundsNeeded:
            raise ValueError("Not enough funds available. Need %f %s, but only %f %s are available" %
                             (fundsNeeded, collateral_asset["symbol"], fundsHave, collateral_asset["symbol"]))

        # Borrow
        if self.rpc:
            transaction = self.rpc.borrow_asset(self.config.account,
                                                '{:.{prec}f}'.format(delta_debt, prec=asset["precision"]),
                                                symbol,
                                                '{:.{prec}f}'.format(amount_of_collateral, prec=collateral_asset["precision"]),
                                                not (self.safe_mode or self.propose_only))
        elif self.config.wif:
            s = {'fee': {'amount': 0, 'asset_id': '1.3.0'},
                 'delta_debt': {'amount': int(delta_debt * 10 ** asset["precision"]),
                                'asset_id': asset["id"]},
                 'delta_collateral': {'amount': int(amount_of_collateral * 10 ** collateral_asset["precision"]),
                                      'asset_id': collateral_asset["id"]},
                 'funding_account': self.myAccount["id"],
                 'extensions': []}
            ops = [transactions.Operation(transactions.Call_order_update(**s))]
            ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction

    def adjust_collateral_ratio(self, symbol, target_collateral_ratio):
        """ Adjust the collataral ratio of a debt position

            :param float amount: Amount to borrow (denoted in 'asset')
            :param str symbol: Asset to borrow
            :param float target_collateral_ratio: desired collateral ratio
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        return self.adjust_debt(0, symbol, target_collateral_ratio)

    def borrow(self, amount, symbol, collateral_ratio):
        """ Borrow bitassets/smartcoins from the network by putting up
            collateral in a CFD at a given collateral ratio.

            :param float amount: Amount to borrow (denoted in 'asset')
            :param str symbol: Asset to borrow
            :param float collateral_ratio: Collateral ratio to borrow at
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available

            Example Output:

            .. code-block:: js

                {
                    "ref_block_num": 14705,
                    "signatures": [],
                    "extensions": [],
                    "expiration": "2016-01-11T15:14:30",
                    "operations": [
                        [
                            3,
                            {
                                "funding_account": "1.2.282",
                                "delta_collateral": {
                                    "amount": 1080540000,
                                    "asset_id": "1.3.0"
                                },
                                "extensions": [],
                                "delta_debt": {
                                    "amount": 10000,
                                    "asset_id": "1.3.106"
                                },
                                "fee": {
                                    "amount": 100000,
                                    "asset_id": "1.3.0"
                                }
                            }
                        ]
                    ],
                    "ref_block_prefix": 1284843328
                }


        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        # We sell quote and pay with base
        asset = self._get_asset(symbol)
        if "bitasset_data_id" not in asset:
            raise ValueError("%s is not a bitasset!" % symbol)
        bitasset = self.getObject(asset["bitasset_data_id"])

        # Check minimum collateral ratio
        backing_asset_id = bitasset["options"]["short_backing_asset"]
        maintenance_col_ratio = bitasset["current_feed"]["maintenance_collateral_ratio"] / 1000
        if maintenance_col_ratio > collateral_ratio:
            raise ValueError("Collateral Ratio has to be higher than %5.2f" % maintenance_col_ratio)

        # Derive Amount of Collateral
        collateral_asset = self._get_asset(backing_asset_id)
        settlement_price = self._get_price(bitasset["current_feed"]["settlement_price"])
        amount_of_collateral = amount * collateral_ratio / settlement_price

        # Verify that enough funds are available
        balances = self.returnBalances()
        fundsNeeded = amount_of_collateral + self.returnFees()["call_order_update"]["fee"]
        fundsHave = balances[collateral_asset["symbol"]]
        if fundsHave <= fundsNeeded:
            raise ValueError("Not enough funds available. Need %f %s, but only %f %s are available" %
                             (fundsNeeded, collateral_asset["symbol"], fundsHave, collateral_asset["symbol"]))

        # Borrow
        if self.rpc:
            transaction = self.rpc.borrow_asset(self.config.account,
                                                '{:.{prec}f}'.format(amount, prec=asset["precision"]),
                                                symbol,
                                                '{:.{prec}f}'.format(amount_of_collateral, prec=collateral_asset["precision"]),
                                                not (self.safe_mode or self.propose_only))
        elif self.config.wif:
            s = {'fee': {'amount': 0, 'asset_id': '1.3.0'},
                 'delta_debt': {'amount': int(amount * 10 ** asset["precision"]),
                                'asset_id': asset["id"]},
                 'delta_collateral': {'amount': int(amount_of_collateral * 10 ** collateral_asset["precision"]),
                                      'asset_id': collateral_asset["id"]},
                 'funding_account': self.myAccount["id"],
                 'extensions': []}
            ops = [transactions.Operation(transactions.Call_order_update(**s))]
            ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction

    def cancel(self, orderNumber):
        """ Cancels an order you have placed in a given market. Requires
            only the "orderNumber". An order number takes the form
            ``1.7.xxx``.

            :param str orderNumber: The Order Object ide of the form ``1.7.xxxx``
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        if self.rpc:
            transaction = self.rpc.cancel_order(orderNumber, not (self.safe_mode or self.propose_only))
        elif self.config.wif:
            s = {"fee": {"amount": 0, "asset_id": "1.3.0"},
                 "fee_paying_account": self.myAccount["id"],
                 "order": orderNumber,
                 "extensions": []
                 }
            ops = [transactions.Operation(transactions.Limit_order_cancel(**s))]
            ops = transactions.addRequiredFees(self.ws, ops, "1.3.0")
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction

    def withdraw(self, currency, amount, address):
        """ This Method makes no sense in a decentralized exchange
        """
        raise NotImplementedError("No withdrawing from the DEX! "
                                  "Please use 'transfer'!")

    def get_lowest_ask(self, currencyPair="all"):
        """ Returns the lowest asks (including amount) for the selected
            markets.

            :param str currencyPair: Market for which to get the lowest ask
            :return: lowest asks and amounts
            :rtype: json

            .. code-block:: js

                {'TRADE.BTC_BTC': [0.8695652173913043, 0.0207]}

        """
        orders = self.returnOrderBook(currencyPair, limit=1)
        r = {}
        for market in orders:
            if len(orders[market]["asks"]) > 0:
                r[market] = orders[market]["asks"][0]
        return r

    def get_lowest_bid(self, currencyPair="all"):
        """ Returns the highest bids (including amount) for the selected
            markets.

            :param str currencyPair: Market for which to get the highest bid
            :return: highest bid and amounts
            :rtype: json

            Example:

            .. code-block:: js

                {'TRADE.BTC_BTC': [1.0055304172951232, 0.009945]}

        """
        orders = self.returnOrderBook(currencyPair, limit=1)
        r = {}
        for market in orders:
            if len(orders[market]["bids"]) > 0:
                r[market] = orders[market]["bids"][0]
        return r

    def get_bids_more_than(self, market, price, limit=25):
        """ Returns those bids (order ids) that have a price more than ``price``
            together with volume and actual price.

            :param str market: Market to consider
            :param float price: Price threshold
            :param number limit: Limit to x bids (defaults to 25)

            Output format:

            .. code-block:: js

                [[price, volume, id], [price, volume, id], ...]

            Example output:

            .. code-block:: js

                {
                    [
                        0.9945,
                        0.01,
                        "1.7.32504"
                    ],
                    [
                        0.9900000120389315,
                        0.79741296,
                        "1.7.25548"
                    ]
                }
        """
        orders = self.returnOrderBook(market, limit)
        bids = []
        for o in orders[market]["bids"]:
            if o[0] > price:
                bids.append(o)
        return bids

    def get_asks_less_than(self, market, price, limit=25):
        """ Returns those asks (order ids) that have a price less than ``price``
            together with volume and actual price.

            :param str market: Market to consider
            :param float price: Price threshold
            :param number limit: Limit to x bids (defaults to 25)

            Output format:

            .. code-block:: js

                [[price, volume, id], [price, volume, id], ...]

            Example output:

            .. code-block:: js

                {
                    [
                        0.9945,
                        0.01,
                        "1.7.32504"
                    ],
                    [
                        0.9900000120389315,
                        0.79741296,
                        "1.7.25548"
                    ]
                }
        """
        orders = self.returnOrderBook(market, limit)
        asks = []
        for o in orders[market]["asks"]:
            if o[0] < price:
                asks.append(o)
        return asks

    def get_my_bids_more_than(self, market, price):
        """ This call will return those open orders that have a price
            that is more than ``price``
        """
        myOrders = self.returnOpenOrders(market)
        r = []
        for order in myOrders[market]:
            if order["type"] == "buy" and order["rate"] < price:
                r.append(order)
        return r

    def get_my_asks_less_than(self, market, price):
        """ This call will return those open orders that have a price
            that is less than ``price``
        """
        myOrders = self.returnOpenOrders(market)
        r = []
        for order in myOrders[market]:
            if order["type"] == "sell" and order["rate"] > price:
                r.append(order)
        return r

    def get_my_bids_out_of_range(self, market, price, tolerance):
        """ This call will return those open bid orders that have a price
            that is more than ``tolerance`` away from price
        """
        myOrders = self.returnOpenOrders(market)
        r = []
        for order in myOrders[market]:
            if order["type"] == "buy" and math.fabs(order["rate"] - price) > tolerance:
                r.append(order)
        return r

    def get_my_asks_out_of_range(self, market, price, tolerance):
        """ This call will return those open ask orders that have a price
            that is more than ``tolerance`` away from price
        """
        myOrders = self.returnOpenOrders(market)
        r = []
        for order in myOrders[market]:
            if order["type"] == "sell" and math.fabs(order["rate"] - price) > tolerance:
                r.append(order)
        return r

    def cancel_bids_more_than(self, market, price):
        orders = self.get_my_bids_more_than(market, price)
        canceledOrders = []
        for order in orders:
            self.cancel(order["orderNumber"])
            canceledOrders.append(order["orderNumber"])
        return canceledOrders

    def cancel_asks_less_than(self, market, price):
        orders = self.get_my_asks_less_than(market, price)
        canceledOrders = []
        for order in orders:
            self.cancel(order["orderNumber"])
            canceledOrders.append(order["orderNumber"])
        return canceledOrders

    def cancel_bids_out_of_range(self, market, price, tolerance):
        orders = self.get_my_bids_out_of_range(market, price, tolerance)
        canceledOrders = []
        for order in orders:
            self.cancel(order["orderNumber"])
            canceledOrders.append(order["orderNumber"])
        return canceledOrders

    def cancel_asks_out_of_range(self, market, price, tolerance):
        orders = self.get_my_asks_out_of_range(market, price, tolerance)
        canceledOrders = []
        for order in orders:
            self.cancel(order["orderNumber"])
            canceledOrders.append(order["orderNumber"])
        return canceledOrders

    def propose_all(self, expiration=None, proposer=None):
        """ If ``proposal_only`` is set True, this method needs to be
            called to **actuctually** propose the operations on the
            chain.

            :param time expiration: expiration time formated as ``%Y-%m-%dT%H:%M:%S`` (defaults to 24h)
            :param string proposer: name of the account that pays the proposer fee
        """
        if not proposer:
            proposer = self.config.account
        if not expiration:
            expiration = datetime.utcfromtimestamp(time.time() + 60 * 60 * 24).strftime('%Y-%m-%dT%H:%M:%S')
        account = self.ws.get_account(proposer)
        proposal = Proposal(self)
        return proposal.propose_operations(self.propose_operations,
                                           expiration,
                                           account["id"],
                                           broadcast=not self.safe_mode)

    def proposals_clear(self):
        """ Clear stored proposals
        """
        self.propose_operations = []

    def fund_fee_pool(self, symbol, amount):
        """ Fund the fee pool of an asset with BTS

            :param str symbol: Symbol of the asset to fund
            :param float amount: Amount of BTS to use for funding fee pool
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        if self.rpc:
            transaction = self.rpc.fund_asset_fee_pool(self.config.account, symbol, amount, not (self.safe_mode or self.propose_only))
        elif self.config.wif:
            asset = self._get_asset(symbol)
            s = {"fee": {"amount": 0,
                         "asset_id": "1.3.0"
                         },
                 "from_account": self.myAccount["id"],
                 "asset_id": asset["id"],
                 "amount": int(amount * 10 ** asset["precision"]),
                 "extensions": []
                 }
            ops = [transactions.Operation(transactions.Asset_fund_fee_pool(**s))]
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction

    def transfer(self, amount, symbol, recepient, memo=""):
        """ Fund the fee pool of an asset with BTS

            :param float amount: Amount to transfer
            :param str symbol: Asset to transfer ("SBD" or "STEEM")
            :param str recepient: Recepient of the transfer
            :param str memo: (Optional) Memo attached to the transfer

            If you want to use a memo you need to specify `memo_wif` in
            the configuration (similar to `wif`).
        """
        if self.safe_mode:
            log.warn("Safe Mode enabled! Not broadcasting anything!")
        if self.rpc:
            transaction = self.rpc.transfer(
                self.config.account,
                recepient,
                amount,
                symbol,
                memo,
                not (self.safe_mode or self.propose_only)
            )
        elif self.config.wif:
            from_account = self.myAccount
            to_account = self.ws.get_account(recepient)
            asset = self._get_asset(symbol)
            s = {
                "fee": {"amount": 0,
                        "asset_id": "1.3.0"
                        },
                "from": from_account["id"],
                "to": to_account["id"],
                "amount": {"amount": int(amount * 10 ** asset["precision"]),
                           "asset_id": asset["id"]
                           }
            }
            if memo:
                if not self.config.memo_wif:
                    print("Missing memo private key! "
                          "Please define `memo_wif` in your configuration")
                    return
                import random
                nonce = str(random.getrandbits(64))
                encrypted_memo = Memo.encode_memo(PrivateKey(self.config.memo_wif),
                                                  PublicKey(to_account["options"]["memo_key"]),
                                                  nonce,
                                                  memo)
                memoStruct = {"from": from_account["options"]["memo_key"],
                              "to": to_account["options"]["memo_key"],
                              "nonce": nonce,
                              "message": encrypted_memo,
                              "chain": "BTS"}
                s["memo"] = transactions.Memo(**memoStruct)

            ops = [transactions.Operation(transactions.Transfer(**s))]
            transaction = self.executeOps(ops)
        else:
            raise NoWalletException()

        if self.propose_only:
            [self.propose_operations.append(o) for o in transaction["operations"]]
            return self.propose_operations
        else:
            return transaction
