import json
from functools import partial
import warnings
import logging
log = logging.getLogger(__name__)


try:
    from autobahn.asyncio.websocket import WebSocketClientProtocol
except ImportError:
    raise ImportError("Missing dependency 'autobahn'.")


class BitSharesWebsocketProtocol(WebSocketClientProtocol):
    """ Graphene Websocket Protocol is the class that will be used
        within the websocket subsystem Autobahn to interact with your
        API on messages, notifications, and events.

        This class handles the actual calls and graphene-specific
        behavior.
    """

    #: loop will be used to indicate the loss of connection
    loop = None

    #: Database callbacks and IDs for object subscriptions
    database_callbacks = {}
    database_callbacks_ids = {}

    #: Accounts and callbacks for account updates
    accounts = []
    accounts_callback = None

    #: Markets to subscribe to
    markets = []

    #: Assets to subscribe to
    assets = []

    #: Storage of Objects to reduce latency and load
    objectMap = None

    #: Event Callback registrations and fnts
    onEventCallbacks = {}

    #: Registered APIs with corresponding API-IDs
    api_ids    = {}

    #: Incremental Request ID and request storage (FIXME: request storage
    #: is not cleaned up)
    request_id = 0
    requests   = {}

    def __init__(self):
        pass

    def _get_request_id(self):
        self.request_id += 1
        return self.request_id

    """ Basic RPC connection
    """
    def wsexec(self, params, callback=None):
        """ Internally used method to execute calls

            :param json params: parameters defining the actual call
            :param fnt callback: Callback to be executed upon receiption
                                 of the answer (defaults to ``None``)
        """
        request = {"request" : {}, "callback" : None}
        request["id"] = self._get_request_id()
        request["request"]["id"] = self.request_id
        request["request"]["method"] = "call"
        request["request"]["params"] = params
        request["callback"] = callback
        self.requests.update({self.request_id: request})
        log.debug(request["request"])
        self.sendMessage(json.dumps(request["request"]).encode('utf8'))

    def register_api(self, name):
        """ Register to an API of graphene

            :param str name: Name of the API (e.g. database, history,
                             ...)
        """
        self.wsexec([1, name, []], [partial(self._set_api_id, name)])

    def _set_api_id(self, name, data):
        """ Set the API id as returned from the server

            :param str name: Name of the API
            :param int data: API id as returned by the server

        """
        self.api_ids.update({name : data})
        if name == "database":
            self.eventcallback("registered-database")
        elif name == "history":
            self.eventcallback("registered-history")
        elif name == "network_broadcast":
            self.eventcallback("registered-network-broadcast")
        elif name == "network_node":
            self.eventcallback("registered-network-node")

    def _login(self):
        """ Login to the API
        """
        log.info("login")
        self.wsexec([1, "login", [self.username, self.password]])

    """ Subscriptions
    """
    def subscribe_to_accounts(self, account_ids, *args):
        """ Subscribe to account ids

            :param account_ids: Account ids to register to
            :type account_ids: Array of account IDs

        """
        log.info("subscribe_to_accounts")
        self.wsexec([0, "get_full_accounts", [account_ids, True]])

    def subscribe_to_markets(self, dummy=None):
        """ Subscribe to the markets as defined in ``self.markets``.
        """
        log.info("subscribe_to_markets")
        for m in self.markets:
            market = self.markets[m]
            self.wsexec([0, "subscribe_to_market",
                         [self._get_request_id(),
                          market["quote"],
                          market["base"]]])

    def subscribe_to_objects(self, *args):
        """ Subscribe to objects as described in

            * ``self.database_callbacks``
            * ``self.accounts``
            * ``self.assets``

            and set the subscription callback.
        """
        log.info("subscribe_to_objects")
        handles = []
        for handle in self.database_callbacks:
            handles.append(partial(self.getObject, handle))
            self.database_callbacks_ids.update({
                handle: self.database_callbacks[handle]})

        asset_ids = set()
        for m in self.assets:
            asset_ids.add(m["id"])
            if "bitasset_data_id" in m:
                asset_ids.add(m["bitasset_data_id"])
            if "dynamic_asset_data_id" in m:
                asset_ids.add(m["dynamic_asset_data_id"])
        handles.append(partial(self.getObjects, list(asset_ids)))

        if self.accounts:
            handles.append(partial(self.subscribe_to_accounts, self.accounts))
        self.wsexec([self.api_ids["database"],
                     "set_subscribe_callback",
                     [self._get_request_id(), False]], handles)

    """ Objects
    """
    def getObject(self, oid, callback=None, *args):
        """ Get an Object from the internal object storage if available
            or otherwise retrieve it from the API.

            :param object-id oid: Object ID to retrieve
            :param fnt callback: Callback to call if object has been received
        """
        self.getObjects([oid], callback, *args)

    def getObjects(self, oids, callback=None, *args):
        # Are they stored in memory already?
        for oid in oids:
            if (self.objectMap and
                    oid in self.objectMap and
                    callable(callback)):
                callback(self.objectMap[oid])
                oids.remove(oid)
        # Let's get those that we haven't found in memory!
        if oids:
            self.wsexec([self.api_ids["database"],
                         "get_objects",
                         [oids]], callback)

    def setObject(self, oid, data):
        """ Set Object in the internal Object Storage
        """
        self.setObjects([oid], [data])

    def setObjects(self, oids, datas):
        if self.objectMap is None:
            return

        for i, oid in enumerate(oids):
            self.objectMap[oid] = datas[i]

    """ Callbacks and dispatcher
    """
    def eventcallback(self, name):
        """ Call an event callback

            :param str name: Name of the event
        """
        if (name in self.onEventCallbacks and
           callable(self.onEventCallbacks[name])):
            self.onEventCallbacks[name](self)

    def dispatchNotice(self, notice):
        """ Main Message Dispatcher for notifications as called by
            ``onMessage``. This dispatcher will separated object,
            account and market updates from each other and call the
            corresponding callbacks.

            :param json notice: Notice from the API

        """
        if "id" not in notice:
            return
        oid = notice["id"]
        [inst, _type, _id] = oid.split(".")
        account_ids = []
        for a in self.accounts :
            account_ids.append("2.6.%s" % a.split(".")[2])  # account history
            account_ids.append("1.2.%s" % a.split(".")[2])  # account
        try:
            " Object Subscriptions "
            if (oid in self.database_callbacks_ids and
               callable(self.database_callbacks_ids[oid])):
                self.database_callbacks_ids[oid](self, notice)

            " Account Notifications "
            if (callable(self.accounts_callback) and
                    (oid in account_ids or  # account updates
                     inst == "1" and _type == "10")):  # proposals
                self.accounts_callback(notice)

            " Market notifications "
            if inst == "1" and _type == "7":
                for m in self.markets:
                    market = self.markets[m]
                    if not callable(market["callback"]):
                        continue
                    if(((market["quote"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["base"] == notice["sell_price"]["base"]["asset_id"]) or
                       (market["base"] == notice["sell_price"]["quote"]["asset_id"] and
                       market["quote"] == notice["sell_price"]["base"]["asset_id"]))):
                        market["callback"](self, notice)

            " Asset notifications "
            if (inst == "1" and _type == "3" or  # Asset itself
                    # bitasset and dynamic data
                    inst == "2" and (_type == "4" or _type == "3")):
                for asset in self.assets:
                    if not callable(asset["callback"]):
                        continue
                    if (asset.get("id") == notice["id"] or
                            asset.get("bitasset_data_id", None) == notice["id"] or
                            asset.get("dynamic_asset_data_id", None) == notice["id"]):
                        asset["callback"](self, notice)

        except:
            import traceback
            log.error('Error dispatching notice: %s' % str(traceback.format_exc()))

    def onConnect(self, response):
        """ Is executed on successful connect. Calls event
            ``connection-init``.
        """
        self.request_id = 1
        log.debug("Server connected: {0}".format(response.peer))
        self.eventcallback("connection-init")

    def onOpen(self):
        """ Called if connection Opened successfully. Logs into the API,
            requests access to APIs and calls event
            ``connection-opened``.
        """
        log.debug("WebSocket connection open.")
        self._login()

        " Register with database "
        self.wsexec([1, "database", []], [
            partial(self._set_api_id, "database"),
            self.subscribe_to_objects,
            self.subscribe_to_markets])

        self.register_api("history")
#       self.register_api("network_node")
        self.register_api("network_broadcast")
        self.eventcallback("connection-opened")

    def onMessage(self, payload, isBinary):
        """ Main websocket message dispatcher.

            This message separates distinct client initiated responses
            from server initiated event-driven notifications and either
            calls the corresponding callback or the notification
            dispatcher.

            :param binary payload: data received through the connection
            :param bool isBinary: Flag to indicate binary nature of the
                                  payload
        """
        res = json.loads(payload.decode('utf8'))
        log.debug(res)
        if "error" not in res:
            " Resolve answers from RPC calls "
            if "id" in res:
                if res["id"] not in self.requests:
                    log.warning("Received answer to an unknown request?!")
                else:
                    callbacks = self.requests[res["id"]]["callback"]
                    if callable(callbacks):
                        callbacks(res["result"])
                    elif isinstance(callbacks, list):
                        for callback in callbacks:
                            callback(res["result"])
            elif "method" in res:
                " Run registered call backs for individual object notices "
                if res["method"] == "notice":
                    [self.setObject(notice["id"], notice)
                        for notice in res["params"][1][0] if "id" in notice]
                    [self.dispatchNotice(notice)
                        for notice in res["params"][1][0] if "id" in notice]
        else:
            log.error("Error! ", res)

    def setLoop(self, loop):
        """ Define the asyncio loop so that it can be halted on
            disconnects
        """
        self.loop = loop

    def connection_lost(self, errmsg):
        """ Is called if the connection is lost. Calls event
            ``connection-closed`` and closes the asyncio main loop.
        """
        log.info("WebSocket connection closed: {0}".format(errmsg))
        self.loop.stop()
        self.eventcallback("connection-closed")

    def onClose(self, wasClean, code, reason):
        self.connection_lost(reason)

    """ L E G A C Y - C A L L S
    """
    def getAccountHistory(self, account_id, callback,
                          start="1.11.0", stop="1.11.0", limit=100):
        """ Get Account history History and call callback

            :param account-id account_id: Account ID to read the history for
            :param fnt callback: Callback to execute with the response
            :param historyID start: Start of the history (defaults to ``1.11.0``)
            :param historyID stop: Stop of the history (defaults to ``1.11.0``)
            :param historyID stop: Limit entries by (defaults to ``100``, max ``100``)
            :raises ValueError: if the account id is incorrectly formatted
        """
        warnings.warn(
            "getAccountHistory is deprecated! "
            "Use client.ws.get_account_history() instead",
            DeprecationWarning
        )
        if account_id[0:4] == "1.2." :
            self.wsexec([self.api_ids["history"],
                        "get_account_history",
                         [account_id, start, 100, stop]],
                        callback)
        else :
            raise ValueError("getAccountHistory expects an account" +
                             "id of the form '1.2.x'!")

    def getAccountProposals(self, account_ids, callback):
        """ Get Account Proposals and call callback

            :param array account_ids: Array containing account ids
            :param fnt callback: Callback to execute with the response

        """
        warnings.warn(
            "getAccountProposals is deprecated! "
            "Use client.ws.get_proposed_transactions() instead",
            DeprecationWarning
        )
        self.wsexec([self.api_ids["database"],
                    "get_proposed_transactions",
                     account_ids],
                    callback)
