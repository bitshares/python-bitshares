*****************
Graphene Exchange
*****************

This module simplyfies the development of trading bots by adding an
abstraction layer to deal with blockchain specific APIs and offers a
simpliefied API that is commonly used by many exchanges (e.g. Poloniex).

The exchange module knows two modes:

* **RPC to cli-wallet**
 
  This mode performs transaction construction and
  signing in using the cli_wallet. It connects to it using Remote
  Procedure Calls (RPC) and requires the **active** private key of the
  trading account to be installed in the cli_wallet with ``import_key
  <account> <wif>``

* **Transaction Signing**:
 
  This mode performs everything in python and
  does **not** depend on a cli_wallet connection. It requires the the
  **active** private key is provided in the configuration.

Usage 1
#######

In this example, we call some of the calls available to the exchange
module. This example can be run **safely** by any one since the Exchange
module is instanciated with ``safe_mode=True``.
Note that you will get an error because the private key does not give
access to the provided example account.

.. code-block:: python 

    from grapheneexchange.exchange import GrapheneExchange
    from pprint import pprint


    class Config():
        witness_url           = "wss://bitshares.openledger.info/ws"
        witness_user          = ""
        witness_password      = ""

        watch_markets         = ["USD_BTS", "GOLD_BTS"]
        market_separator      = "_"
        account               = "xeroc"
        wif                   = "BTS5Bfhb7aRCWUTh1CkrSXUyRJsSqqzD1rQCVkxmrHGfCF8HuktfR"

    if __name__ == '__main__':
        dex   = GrapheneExchange(Config, safe_mode=True)
        pprint((dex.returnTradeHistory("USD_BTS")))
        pprint((dex.returnTicker()))
        pprint((dex.return24Volume()))
        pprint((dex.returnOrderBook("USD_BTS")))
        pprint((dex.returnBalances()))
        pprint((dex.returnOpenOrders("all")))
        pprint(dex.buy("USD_BTS", 0.001, 10))
        pprint(dex.sell("USD_BTS", 0.001, 10))
        pprint(dex.close_debt_position("USD"))
        pprint(dex.adjust_debt(10, "USD", 3.0))
        pprint(dex.borrow(10, "USD", 3.0))
        pprint(dex.cancel("1.7.1111"))

Usage 2
#######

A simple example for a bot can be found in
`scripts/exchange-bridge-market-maker/` and works like this:

.. code-block:: python 

    from grapheneexchange import GrapheneExchange
    import config
    dex = GrapheneExchange(config, safe_mode=False)
    #: Close all orders that have been put in those markets previously
    orders = dex.returnOpenOrders()
    for m in orders:
        for o in orders[m]:
            print(" - %s" % o["orderNumber"])
            dex.cancel(o["orderNumber"])
    #: Buy and Sell Prices
    buy_price  = 1 - config.bridge_spread_percent / 200
    sell_price = 1 + config.bridge_spread_percent / 200
    #: Amount of Funds available for trading (per asset)
    balances = dex.returnBalances()
    asset_ids = []
    amounts = {}
    for market in config.watch_markets :
        quote, base = market.split(config.market_separator)
        asset_ids.append(base)
        asset_ids.append(quote)
    assets_unique = list(set(asset_ids))
    for a in assets_unique:
        if a in balances :
            amounts[a] = balances[a] * config.bridge_amount_percent / 100 / asset_ids.count(a)
    for m in config.watch_markets:
        quote, base = m.split(config.market_separator)
        if quote in amounts :
            print(" - Selling %f %s for %s @%f" % (amounts[quote], quote, base, sell_price))
            dex.sell(m, sell_price, amounts[quote])
        if base in amounts :
            print(" - Buying %f %s with %s @%f" % (amounts[base], base, quote, buy_price))
            dex.buy(m, buy_price, amounts[base] * buy_price)

Specifications
##############

GrapheneExchange
****************

.. autoclass:: grapheneexchange.exchange.GrapheneExchange
    :members:

Configuration
*************

.. autoclass:: grapheneexchange.exchange.ExampleConfig
    :members:
