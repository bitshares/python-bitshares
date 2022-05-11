# -*- coding: utf-8 -*-
import json
import time
import signal
import logging
import threading
import websocket
import traceback

from itertools import cycle
from events import Events
from .exceptions import NumRetriesReached

# This restores the default Ctrl+C signal handler, which just kills the process
signal.signal(signal.SIGINT, signal.SIG_DFL)

log = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)


class BitSharesWebsocket(Events):
    """
    Create a websocket connection and request push notifications.

    :param str urls: Either a single Websocket URL, or a list of URLs
    :param str user: Username for Authentication
    :param str password: Password for Authentication
    :param list accounts: list of account names or ids to get push notifications for
    :param list markets: list of asset_ids, e.g. ``[['1.3.0', '1.3.121']]``
    :param list objects: list of objects id's you'd like to be notified when changing
    :param int keep_alive: seconds between a ping to the backend (defaults to 25seconds)

    After instanciating this class, you can add event slots for:

    * ``on_tx``
    * ``on_object``
    * ``on_block``
    * ``on_account``
    * ``on_market``

    which will be called accordingly with the notification
    message received from the BitShares node:

    .. code-block:: python

        ws = BitSharesWebsocket(
            "wss://node.testnet.bitshares.eu",
            objects=["2.0.x", "2.1.x", "1.3.x"]
        )
        ws.on_object += print
        ws.run_forever()

    Notices:

    * ``on_account``:

        .. code-block:: js

            {'id': '2.6.29',
             'lifetime_fees_paid': '44257768405',
             'most_recent_op': '2.9.1195638',
             'owner': '1.2.29',
             'pending_fees': 0,
             'pending_vested_fees': 100,
             'total_core_in_orders': '6788960277634',
             'total_ops': 505865}

    * ``on_block``:

        .. code-block:: js

            '0062f19df70ecf3a478a84b4607d9ad8b3e3b607'

    * ``on_tx``:

        .. code-block:: js

            {'expiration': '2017-02-23T09:33:22',
             'extensions': [],
             'operations': [[0,
                             {'amount': {'amount': 100000, 'asset_id': '1.3.0'},
                              'extensions': [],
                              'fee': {'amount': 100, 'asset_id': '1.3.0'},
                              'from': '1.2.29',
                              'to': '1.2.17'}]],
             'ref_block_num': 62001,
             'ref_block_prefix': 390951726,
             'signatures': ['20784246dc1064ed5f87dbbb9aaff3fcce052135269a8653fb500da46e7068bec56e85ea997b8d250a9cc926777c700eed41e34ba1cabe65940965ebe133ff9098']}

    * ``on_market``:

        .. code-block:: js

            ['1.7.68612']
    """

    __events__ = ["on_tx", "on_object", "on_block", "on_account", "on_market"]

    def __init__(
        self,
        urls,
        user="",
        password="",
        *args,
        accounts=None,
        markets=None,
        objects=None,
        on_tx=None,
        on_object=None,
        on_block=None,
        on_account=None,
        on_market=None,
        keep_alive=25,
        num_retries=-1,
        **kwargs
    ):

        self.num_retries = num_retries
        self.keepalive = None
        self._request_id = 0
        self.ws = None
        self.user = user
        self.password = password
        self.keep_alive = keep_alive
        self.run_event = threading.Event()
        if isinstance(urls, cycle):
            self.urls = urls
        elif isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])

        # Instanciate Events
        Events.__init__(self)
        self.events = Events()

        # Store the objects we are interested in
        self.subscription_accounts = accounts or []
        self.subscription_markets = markets or []
        self.subscription_objects = objects or []

        if on_tx:
            self.on_tx += on_tx
        if on_object:
            self.on_object += on_object
        if on_block:
            self.on_block += on_block
        if on_account:
            self.on_account += on_account
        if on_market:
            self.on_market += on_market

    def cancel_subscriptions(self):
        self.cancel_all_subscriptions()

    def on_open(self, *args, **kwargs):
        """
        This method will be called once the websocket connection is established. It
        will.

        * login,
        * register to the database api, and
        * subscribe to the objects defined if there is a
          callback/slot available for callbacks
        """
        self.login(self.user, self.password, api_id=1)
        self.database(api_id=1)
        self.__set_subscriptions()
        self.keepalive = threading.Thread(target=self._ping)
        self.keepalive.start()

    def reset_subscriptions(self, accounts=None, markets=None, objects=None):
        self.subscription_accounts = accounts or []
        self.subscription_markets = markets or []
        self.subscription_objects = objects or []
        self.__set_subscriptions()

    def __set_subscriptions(self):
        self.cancel_all_subscriptions()

        # Subscribe to events on the Backend and give them a
        # callback number that allows us to identify the event

        if len(self.on_object) or len(self.subscription_accounts):
            self.set_subscribe_callback(self.__events__.index("on_object"), False)

        if self.subscription_accounts and self.on_account:
            # Unfortunately, account subscriptions don't have their own
            # callback number
            log.debug("Subscribing to accounts %s" % str(self.subscription_accounts))
            self.get_full_accounts(self.subscription_accounts, True)

        if self.subscription_markets and self.on_market:
            log.debug("Subscribing to markets %s" % str(self.subscription_markets))
            for market in self.subscription_markets:
                # Technially, every market could have it's own
                # callback number
                self.subscribe_to_market(
                    self.__events__.index("on_market"), market[0], market[1]
                )
        if len(self.on_tx):
            self.set_pending_transaction_callback(self.__events__.index("on_tx"))
        if len(self.on_block):
            self.set_block_applied_callback(self.__events__.index("on_block"))

    def _ping(self):
        # We keep the connection alive by requesting a short object
        while not self.run_event.wait(self.keep_alive):
            log.debug("Sending ping")
            self.get_objects(["2.8.0"])

    def process_notice(self, notice):
        """
        This method is called on notices that need processing.

        Here, we call ``on_object`` and ``on_account`` slots.
        """
        id = notice["id"]

        _a, _b, _ = id.split(".")

        if id in self.subscription_objects:
            self.on_object(notice)

        elif ".".join([_a, _b, "x"]) in self.subscription_objects:
            self.on_object(notice)

        elif id[:4] == "2.6.":
            # Treat account updates separately
            self.on_account(notice)

    def on_message(self, reply, *args, **kwargs):
        """
        This method is called by the websocket connection on every message that is
        received.

        If we receive a ``notice``, we hand over post-processing and signalling of
        events to ``process_notice``.
        """
        if isinstance(reply, websocket.WebSocketApp):
            reply = args[0]
        log.debug("Received message: %s" % str(reply))
        data = {}
        try:
            data = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("API node returned invalid format. Expected JSON!")

        if data.get("method") == "notice":
            id = data["params"][0]

            if id >= len(self.__events__):
                log.critical("Received an id that is out of range\n\n" + str(data))
                return

            # This is a "general" object change notification
            if id == self.__events__.index("on_object"):
                # Let's see if a specific object has changed
                for notice in data["params"][1]:
                    try:
                        if "id" in notice:
                            self.process_notice(notice)
                        else:
                            for obj in notice:
                                if "id" in obj:
                                    self.process_notice(obj)
                    except Exception as e:
                        log.critical(
                            "Error in process_notice: {}\n\n{}".format(
                                str(e), traceback.format_exc
                            )
                        )
            else:
                try:
                    callbackname = self.__events__[id]
                    log.debug("Patching through to call %s" % callbackname)
                    [getattr(self.events, callbackname)(x) for x in data["params"][1]]
                except Exception as e:
                    log.critical(
                        "Error in {}: {}\n\n{}".format(
                            callbackname, str(e), traceback.format_exc()
                        )
                    )

    def on_error(self, error, *args, **kwargs):
        """Called on websocket errors."""
        log.exception(error)

    def on_close(self, *args, **kwargs):
        """Called when websocket connection is closed."""
        log.debug("Closing WebSocket connection with {}".format(self.url))

    def run_forever(self, *args, **kwargs):
        """
        This method is used to run the websocket app continuously.

        It will execute callbacks as defined and try to stay connected with the provided
        APIs
        """
        cnt = 0
        while not self.run_event.is_set():
            cnt += 1
            self.url = next(self.urls)
            log.debug("Trying to connect to node %s" % self.url)
            try:
                # websocket.enableTrace(True)
                self.ws = websocket.WebSocketApp(
                    self.url,
                    on_message=self.on_message,
                    on_error=self.on_error,
                    on_close=self.on_close,
                    on_open=self.on_open,
                )
                self.ws.run_forever()
            except websocket.WebSocketException:
                if self.num_retries >= 0 and cnt > self.num_retries:
                    raise NumRetriesReached()

                sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
                if sleeptime:
                    log.warning(
                        "Lost connection to node during wsconnect(): %s (%d/%d) "
                        % (self.url, cnt, self.num_retries)
                        + "Retrying in %d seconds" % sleeptime
                    )
                    time.sleep(sleeptime)

            except KeyboardInterrupt:
                self.ws.keep_running = False
                return

            except Exception as e:
                log.critical("{}\n\n{}".format(str(e), traceback.format_exc()))

    def close(self, *args, **kwargs):
        """Closes the websocket connection and waits for the ping thread to close."""
        self.run_event.set()
        self.ws.close()

        if self.keepalive and self.keepalive.is_alive():
            self.keepalive.join()

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    """ RPC Calls
    """

    def rpcexec(self, payload):
        """
        Execute a call by sending the payload.

        :param dict payload: Payload data
        :raises ValueError: if the server does not respond in proper JSON format
        :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))
        self.ws.send(json.dumps(payload, ensure_ascii=False).encode("utf8"))

    def __getattr__(self, name):
        """Map all methods to RPC calls and pass through the arguments."""
        if name in self.__events__:
            return getattr(self.events, name)

        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:
                if "api" in kwargs:
                    if kwargs["api"] in self.api_id and self.api_id[kwargs["api"]]:
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        raise ValueError(
                            "Unknown API! "
                            "Verify that you have registered to %s" % kwargs["api"]
                        )
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {
                "method": "call",
                "params": [api_id, name, list(args)],
                "jsonrpc": "2.0",
                "id": self.get_request_id(),
            }
            r = self.rpcexec(query)
            return r

        return method
