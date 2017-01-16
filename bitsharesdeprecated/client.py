from grapheneapi.grapheneapi import GrapheneApi as BitSharesAPI
from .websocket import BitSharesWebsocket
from collections import OrderedDict

import logging
log = logging.getLogger(__name__)


class ExampleConfig():
    """ The behavior of your program (e.g. reactions on messages) can be
        defined in a separated class (here called ``Config()``. It contains
        the wallet and witness connection parameters:

        The config class is used to define several attributes *and*
        methods that will be used during API communication. This is
        particularily useful when dealing with event-driven websocket
        notifications.

        **RPC-Only Connections**:

        The simples setup for this class is a simply RPC:

        .. code-block:: python

            class Config():
                wallet_host = "localhost"
                wallet_port = 8092
                wallet_user = ""
                wallet_password = ""

        and allows the use of rpc commands similar to the
        ``BitSharesAPI`` class:

        .. code-block:: python

            graphene = BitSharesClient(Config)
            print(graphene.rpc.info())
            print(graphene.rpc.get_account("init0"))
            print(graphene.rpc.get_asset("USD"))

        All methods within ``graphene.rpc`` are mapped to the
        corresponding RPC call of the wallet and the parameters are
        handed over directly.

        **Additional Websocket Connections**:

        .. code-block:: python

            class Config(GrapheneWebsocketProtocol):  ## Note the dependency
                wallet_host = "localhost"
                wallet_port = 8092
                wallet_user = ""
                wallet_password = ""
                witness_url = "ws://localhost:8090/"
                witness_user = ""
                witness_password = ""

        Some methods will be called automatically from the underlying websocket
        protocol. They all start with ``onXXX`` and are described below.

        .. note:: ``data`` will be the notification from the websocket protocol that
                  caused the call. It will have an object id ``data["id"]`` to identify
                  it!
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

    #: Accounts to watch. Changes on these will result in the method
    #: ``onAccountUpdate()`` to be called
    watch_accounts = ["fabian", "nathan"]

    #: Assets you want to watch. Changes will be used to call
    #: ``onAssetUpdate()``.
    watch_assets = ["USD"]

    #: Markets to watch. Changes to these will result in the method
    #: ``onMarketUpdate()`` to be called
    watch_markets = ["USD:CORE"]

    def onAccountUpdate(self, data):
        """ Account updates will be triggered if attribute
            ``watch_accounts`` is defined and either the corresponding
            object ``1.2.x`` **or** ``2.6.x`` is updated.

            :param json data: notification that triggered the call (see
                              below)

            **Example notifications:**

            .. code-block:: json

                {
                    "most_recent_op": "2.9.252",
                    "pending_fees": 0,
                    "total_core_in_orders": 90000000,
                    "id": "2.6.17",
                    "owner": "1.2.17",
                    "lifetime_fees_paid": "26442269333",
                    "pending_vested_fees": 500000
                }

            .. code-block:: json

                {
                    "options": {
                        "extensions": [],
                        "memo_key": "",
                        "voting_account": "1.2.5",
                        "num_committee": 1,
                        "votes": [
                            "0:11"
                        ],
                        "num_witness": 0
                    },
                    "referrer": "1.2.17",
                    "lifetime_referrer": "1.2.17",
                    "blacklisting_accounts": [],
                    "registrar": "1.2.17",
                    "membership_expiration_date": "1969-12-31T23:59:59",
                    "network_fee_percentage": 2000,
                    "cashback_vb": "1.13.0",
                    "id": "1.2.17",
                    "active": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "address_auths": [],
                        "key_auths": [
                            [
                                "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                1
                            ]
                        ]
                    },
                    "name": "nathan",
                    "referrer_rewards_percentage": 0,
                    "whitelisting_accounts": [],
                    "owner": {
                        "weight_threshold": 1,
                        "account_auths": [],
                        "address_auths": [],
                        "key_auths": [
                            [
                                "GPH6MRyAjQq8ud7hVNYcfnVPJqcVpscN5So8BhtHuGYqET5GDW5CV",
                                1
                            ]
                        ]
                    },
                    "statistics": "2.6.17",
                    "blacklisted_accounts": [],
                    "lifetime_referrer_fee_percentage": 8000
                }
            """
        pass

    def onAssetUpdate(self, data):
        """ This method is called when any of the assets in watch_assets
            changes. The changes of the following objects are monitored:

             * Asset object (``1.3.x``)
             * Dynamic Asset data (``2.3.x``)
             * Bitasset data (``2.4.x``)

             Hence, this method needs to distinguish these three
             objects!

        """
        pass

    def onMarketUpdate(self, data):
        """ This method will be called if a subscribed market sees an
            event (registered to through ``watch_markets``).

            :param json data: notification that caused the call

            Example notification:

            .. code-block:: json

                {
                    "seller": "1.2.17",
                    "id": "1.7.0",
                    "for_sale": 88109000,
                    "deferred_fee": 0,
                    "expiration": "2020-12-23T11:13:42",
                    "sell_price": {
                        "base": {
                            "asset_id": "1.3.1",
                            "amount": 100000000
                        },
                        "quote": {
                            "asset_id": "1.3.0",
                            "amount": 1000000000
                        }
                    }
                }
        """
        pass

    def onBlock(self, data):
        """ Will be triggered on every new block (e.g. change of object
            `2.0.0`)

            :param json data: notification that caused the call

            Example notification:

            .. code-block:: python

                data = {
                    "id": "2.1.0",
                    "dynamic_flags": 0,
                    "current_witness": "1.6.7",
                    "next_maintenance_time": "2015-12-31T00:00:00",
                    "recently_missed_count": 1079135,
                    "current_aslot": 345685,
                    "head_block_id": "00002f5410b2991a7ed64994b6fe08353603a702",
                    "witness_budget": 0,
                    "last_irreversible_block_num": 12107,
                    "head_block_number": 12116,
                    "time": "2015-12-30T10:10:30",
                    "accounts_registered_this_interval": 0,
                    "recent_slots_filled": "340282366920938463463374607431768211455",
                    "last_budget_time": "2015-12-30T09:28:15"
                }
        """
        pass

    def onPropertiesChange(self, data):
        """ Will be triggered every time a parameter of the blockchain
            (e.g. fees or times) changes.

            :param json data: notification that caused the call

            Example notification:

            .. code-block:: python

                {"id":"2.0.0","parameters":{"current_fees":{"parameters":[[0,{"fee":3000000,"price_per_kbyte":2000000}],
                [1,{"fee":1000000}],[2,{"fee":0}],[3,{"fee":100000}],[4,{}],[5,{"basic_fee":9500000,"premium_fee":400000000,
                "price_per_kbyte":200000}],[6,{"fee":100000,"price_per_kbyte":20}],[7,{"fee":600000}],[8,{"membership_annual_fee":400000000,
                "membership_lifetime_fee":2000000000}],[9,{"fee":100000000}],[10,{"symbol3":"100000000000","symbol4":"26000000000",
                "long_symbol":500000000,"price_per_kbyte":20}],[11,{"fee":2000000,"price_per_kbyte":200000}],[12,{"fee":100000000}],
                [13,{"fee":100000000}],[14,{"fee":4000000,"price_per_kbyte":200000}],[15,{"fee":4000000}],[16,{"fee":200000}],
                [17,{"fee":20000000}],[18,{"fee":100000000}],[19,{"fee":10000}],[20,{"fee":1000000000}],[21,{"fee":4000000}],
                [22,{"fee":4000000,"price_per_kbyte":20}],[23,{"fee":200000,"price_per_kbyte":20}],[24,{"fee":200000}],[25,{"fee":200000}],
                [26,{"fee":4000000}],[27,{"fee":0,"price_per_kbyte":20}],[28,{"fee":1000000000}],[29,{"fee":200000}],[30,{"fee":200000}],
                [31,{"fee":4000000}],[32,{"fee":1000000000}],[33,{"fee":200000}],[34,{"fee":200000}],[35,{"fee":200000,"price_per_kbyte":20}],
                [36,{"fee":4000000}],[37,{}],[38,{"fee":1000000,"price_per_kbyte":20}],[39,{"fee":2000000,"price_per_output":2000000}],
                [41,{"fee":2000000}]],"scale":10000},"block_interval":3,"maintenance_interval":3600,"maintenance_skip_slots":3,
                "committee_proposal_review_period":3600,"maximum_transaction_size":98304,"maximum_block_size":2097152,
                "maximum_time_until_expiration":86400,"maximum_proposal_lifetime":2419200,"maximum_asset_whitelist_authorities":10,
                "maximum_asset_feed_publishers":10,"maximum_witness_count":1001,"maximum_committee_count":1001,"maximum_authority_membership":10,
                "reserve_percent_of_fee":2000,"network_percent_of_fee":2000,"lifetime_referrer_percent_of_fee":3000,
                "cashback_vesting_period_seconds":7776000,"cashback_vesting_threshold":10000000,"count_non_member_votes":true,
                "allow_non_member_whitelists":false,"witness_pay_per_block":150000,"worker_budget_per_day":"50000000000",
                "max_predicate_opcode":1,"fee_liquidation_threshold":10000000,"accounts_per_fee_scale":1000,"account_fee_scale_bitshifts":0,
                "max_authority_depth":2,"extensions":[]},"next_available_vote_id":141,"active_committee_members":["1.5.11","1.5.20","1.5.19",
                "1.5.14","1.5.4","1.5.7","1.5.8","1.5.9","1.5.10","1.5.12","1.5.15"],"active_witnesses":["1.6.12","1.6.13","1.6.14","1.6.15",
                "1.6.16","1.6.17","1.6.18","1.6.19","1.6.20","1.6.21","1.6.22","1.6.24","1.6.25","1.6.26","1.6.27","1.6.28","1.6.30","1.6.34",
                "1.6.35","1.6.37","1.6.38","1.6.42","1.6.43","1.6.45","1.6.49"]}

        """
        pass

    def onRegisterHistory(self):
        """ Will be triggered once the websocket subsystem successfully
            subscribed to the `history` API.
        """
        pass

    def onRegisterDatabase(self):
        """ Will be triggered once the websocket subsystem successfully
            subscribed to the `database` API.
        """
        pass

    def onRegisterNetworkNode(self):
        """ Will be triggered once the websocket subsystem successfully
            subscribed to the `network_node` API.
        """
        pass

    def onRegisterNetworkBroadcast(self):
        """ Will be triggered once the websocket subsystem successfully
            subscribed to the `network_broadcast` API.
        """
        pass


class BitSharesClient():
    """ The ``BitSharesClient`` class is an abstraction layer that makes the use of the
        RPC and the websocket interface easier to use. A part of this
        abstraction layer is to simplyfy the usage of objects and have
        an internal objects map updated to reduce unecessary queries
        (for enabled websocket connections). Advanced developers are of
        course free to use the underlying API classes instead as well.

        :param class config: the configuration class

        If a websocket connection is configured, the websocket subsystem
        can be run by:

        .. code-block:: python

            graphene = BitSharesClient(config)
            graphene.run()

    """
    wallet_host = None
    wallet_port = None
    wallet_user = None
    wallet_password = None
    witness_url = None
    witness_user = None
    witness_password = None
    prefix = None

    #: RPC connection to the cli-wallet
    rpc = None

    #: Websocket connection to the witness/full node
    ws = None

    def __init__(self, config):
        """ Initialize configuration
        """
        available_features = dir(config)

        if ("wallet_host" in available_features and
                "wallet_port" in available_features):
            self.wallet_host = config.wallet_host
            self.wallet_port = config.wallet_port

            if ("wallet_user" in available_features and
                    "wallet_password" in available_features):
                self.wallet_user = config.wallet_user
                self.wallet_password = config.wallet_password

            self.rpc = BitSharesAPI(self.wallet_host,
                                    self.wallet_port,
                                    self.wallet_user,
                                    self.wallet_password)
            BitSharesAPI.__init__(self,
                                  self.wallet_host,
                                  self.wallet_port,
                                  self.wallet_user,
                                  self.wallet_password)

            self.core_asset = self.rpc.get_object("1.3.0")[0]

        # Connect to Witness Node
        if "witness_url" in available_features:
            self.witness_url = config.witness_url

            if ("witness_user" in available_features and
                    "witness_password" in available_features):
                self.witness_user = config.witness_user
                self.witness_password = config.witness_password

            self.ws = BitSharesWebsocket(self.witness_url,
                                         self.witness_user,
                                         self.witness_password,
                                         proto=config)

            # Register Call available backs
            if "onPropertiesChange" in available_features:
                self.setObjectCallbacks({"2.0.0": config.onPropertiesChange})
            if "onBlock" in available_features:
                self.setObjectCallbacks({"2.1.0": config.onBlock})
            if ("watch_accounts" in available_features and
                    "onAccountUpdate" in available_features):
                account_ids = []
                for a in config.watch_accounts:
                    account = self.ws.get_account(a)
                    if "id" in account:
                        account_ids.append(account["id"])
                    else:
                        log.warn("Account %s could not be found" % a)
                self.setAccountsDispatcher(account_ids, config.onAccountUpdate)
            if "market_separator" in available_features:
                self.market_separator = config.market_separator
            else:
                self.market_separator = ":"
            if ("watch_markets" in available_features):
                self.markets = {}
                for market in config.watch_markets:
                    try:
                        [quote_symbol, base_symbol] = market.split(self.market_separator)
                    except:
                        raise ValueError("An error has occured trying to " +
                                         "parse the markets! Please " +
                                         "check your values")
                    try:
                        quote = self.ws.get_asset(quote_symbol)
                        base = self.ws.get_asset(base_symbol)
                    except:
                        raise Exception("Couldn't load assets for market %s"
                                        % market)
                    if not quote or not base:
                        raise Exception("Couldn't load assets for market %s"
                                        % market)

                    if "id" in quote and "id" in base:
                        if "onMarketUpdate" in available_features:
                            self.markets.update({
                                market: {"quote": quote["id"],
                                         "base": base["id"],
                                         "base_symbol": base["symbol"],
                                         "quote_symbol": quote["symbol"],
                                         "callback": config.onMarketUpdate}})
                        else:  # No callbacks
                            self.markets.update({
                                market: {"quote": quote["id"],
                                         "base": base["id"],
                                         "base_symbol": base["symbol"],
                                         "quote_symbol": quote["symbol"]}})
                    else:
                        log.warn("Market assets could not be found: %s"
                                 % market)
                self.setMarketCallBack(self.markets)

            if ("watch_assets" in available_features):
                assets = []
                for asset in config.watch_assets:
                    a = self.ws.get_asset(asset)
                    if not a:
                        log.warning("The asset %s does not exist!" % a)

                    if ("onAssetUpdate" in available_features):
                        a["callback"] = config.onAssetUpdate
                    assets.append(a)
                self.setAssetDispatcher(assets)

            if "onRegisterHistory" in available_features:
                self.setEventCallbacks(
                    {"registered-history": config.onRegisterHistory})
            if "onRegisterDatabase" in available_features:
                self.setEventCallbacks(
                    {"registered-database": config.onRegisterDatabase})
            if "onRegisterNetworkNode" in available_features:
                self.setEventCallbacks(
                    {"registered-network-node": config.onRegisterNetworkNode})
            if "onRegisterNetworkBroadcast" in available_features:
                self.setEventCallbacks(
                    {"registered-network-broadcast":
                     config.onRegisterNetworkBroadcast})

            self.core_asset = self.ws.get_object("1.3.0")

        if not self.core_asset:
            raise Exception("Neither WS nor RPC propery configured!")

        if self.core_asset["symbol"] == "BTS":
            self.prefix = "BTS"
        elif self.core_asset["symbol"] == "MUSE":
            self.prefix = "MUSE"
        elif self.core_asset["symbol"] == "TEST":
            self.prefix = "TEST"
        elif self.core_asset["symbol"] == "CORE":
            self.prefix = "GPH"

    """ Get network configuration
    """
    def getChainInfo(self):
        """ Returns some information about the connected chain.

            :return: Blockchain data
            :rtype: json

            .. warning:: Note, this does not verify if the cli-wallet is
                         on the same network as the witness node!

            Example:

            .. code-block:: s

                {'chain_id': 'b8d1603965b3eb1acba27e62ff59f74efa3154d43a4188d381088ac7cdf35539',
                 'core_symbol': 'CORE',
                 'prefix': 'GPH'}

        """
        if self.ws:
            core_asset = self.ws.get_object("1.3.0")
            chain_id = self.ws.get_chain_id()
        elif self.rpc:
            core_asset = self.rpc.get_object("1.3.0")
            chain_id = self.rpc.info()["chain_id"]
        else:
            raise Exception("Neither either ws or rpc connection!")
        return {"prefix": self.prefix,
                "core_symbol": core_asset["symbol"],
                "chain_id": chain_id}

    def getObject(self, oid):
        """ Get an Object either from Websocket store (if available) or
            from RPC connection.
        """
        if self.ws:
            [_instance, _type, _id] = oid.split(".")
            if (not (oid in self.ws.objectMap) or
                    _instance == "1" and _type == "7"):  # force refresh orders
                data = self.ws.get_object(oid)
                self.ws.objectMap[oid] = data
            else:
                data = self.ws.objectMap[oid]
            if len(data) == 1:
                return data[0]
            else:
                return data
        else:
            return self.rpc.get_object(oid)[0]

    def get_object(self, oid):
        """ Identical to ``getObject``
        """
        return self.getObject(oid)

    """ Forward these calls to Websocket API
    """
    def setEventCallbacks(self, callbacks):
        """ Internally used to register subsystem events, such as
            `register-database` to callbacks
        """
        self.ws.setEventCallbacks(callbacks)

    def setAccountsDispatcher(self, accounts, callback):
        """ Internally used to register a account notification dispatcher
        """
        self.ws.setAccountsDispatcher(accounts, callback)

    def setObjectCallbacks(self, callbacks):
        """ Internally used to register object notification callbacks
        """
        self.ws.setObjectCallbacks(callbacks)

    def setMarketCallBack(self, markets):
        """ Internally used to register Market update callbacks
        """
        self.ws.setMarketCallBack(markets)

    def setAssetDispatcher(self, markets):
        """ Internally used to register Market update callbacks
        """
        self.ws.setAssetDispatcher(markets)

    """ Connect to Websocket and run asynchronously
    """
    def connect(self):
        """ Only *connect* to the websocket server. Does **not** run the
            subsystem.
        """
        self.ws.connect()

    def run_forever(self):
        """ Only **run** the subsystem. Requires to run ``connect()``
            first.
        """
        self.ws.run_forever()

    def run(self):
        """ Connect to Websocket server **and** run the subsystem """
        self.connect()
        self.run_forever()
