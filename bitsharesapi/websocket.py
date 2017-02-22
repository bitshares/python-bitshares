import threading
import ssl
import time
import json
import logging
from itertools import cycle
from threading import Thread

from events import Events
import websocket

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)



class NumRetriesReached(Exception):
    pass


class BitSharesWebsocket(Events):
    __events__ = [
        'on_tx',
        'on_object',
        'on_block',
        'on_account',
        'on_market',
    ]

    def __init__(
        self,
        urls,
        user="",
        password="",
        *args,
        accounts=[],
        markets=[],
        objects=[],
        bitshares_instance=None,
        **kwargs
    ):
        """ Create a websocket connection and request push notifications

            :param list accounts: list of account names or ids to get push notifications for
            :param list markets: list of asset_ids, e.g. ``[['1.3.0', '1.3.121']]``
        """

        self._request_id = 0
        self.user = user
        self.password = password
        if isinstance(urls, list):
            self.urls = cycle(urls)
        else:
            self.urls = cycle([urls])

        # This is the shares connection
        self.ws = None

        # We open up another connection for push notifications
        Events.__init__(self, *args, **kwargs)

        self.events = Events()
        self.subscription_accounts = accounts
        self.subscription_markets = markets
        self.subscription_objects = objects

    def on_open(self, ws):
        self.login(self.user, self.password, api_id=1)
        self.database(api_id=1)
        self.cancel_all_subscriptions()
        self.set_subscribe_callback(
            self.__events__.index('on_object'),
            False)

        if len(self.on_block):
            self.set_block_applied_callback(
                self.__events__.index('on_block'))

        if len(self.on_tx):
            self.set_pending_transaction_callback(
                self.__events__.index('on_tx'))

        if len(self.on_block):
            self.set_block_applied_callback(
                self.__events__.index('on_block'))

        if self.subscription_accounts and self.on_account:
            self.accounts = self.get_full_accounts(self.subscription_accounts, True)

        if self.subscription_markets and self.on_market:
            for market in self.subscription_markets:
                self.subscribe_to_market(
                    self.__events__.index('on_market'),
                    market[0], market[1])

        self.keepalive = Thread(
            target=self.get_objects,
            args=(["2.9.0"],)
        ).start()

    def process_notice(self, notice):
        id = notice["id"]
        _a, _b, _ = id.split(".")

        if id in self.subscription_objects:
            self.on_object(notice)

        elif ".".join([_a, _b, "x"]) in self.subscription_objects:
            self.on_object(notice)

        elif id[:4] == "2.6.":
            # Treat account updates separately
            self.on_account(notice)

    def on_message(self, ws, reply, *args):
        data = {}
        try:
            data = json.loads(reply, strict=False)
        except ValueError:
            raise ValueError("Client returned invalid format. Expected JSON!")

        if data.get("method") == "notice":
            id = data["params"][0]
            if id >= len(self.__events__):
                log.critical(
                    "Received an id that is out of range\n\n" +
                    str(data)
                )
                return

            if id == self.__events__.index('on_object'):
                # Let's see if a specific object has changed
                for notice in data["params"][1]:
                    if "id" in notice:
                        self.process_notice(notice)
                    else:
                        for obj in notice:
                            if "id" in obj:
                                self.process_notice(obj)
            else:
                callbackname = self.__events__[id]
                [getattr(self.events, callbackname)(x) for x in data["params"][1]]

    def on_error(self, ws, error):
        log.exception(error)

    def on_close(self, ws):
        log.critical('Closing WebSocket connection')

    def run_forever(self):
        cnt = 0
        cnt += 1
        self.url = next(self.urls)
        log.debug("Trying to connect to node %s" % self.url)
        try:
            # websocket.enableTrace(True)
            self.ws = websocket.WebSocketApp(
                self.url,
                on_message=self.on_message,
                on_data=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
                on_open=self.on_open
            )
            self.ws.run_forever()
        except websocket.WebSocketException as exc:
            if (self.num_retries >= 0 and cnt > self.num_retries):
                raise NumRetriesReached()

            sleeptime = (cnt - 1) * 2 if cnt < 10 else 10
            if sleeptime:
                log.warning(
                    "Lost connection to node during wsconnect(): %s (%d/%d) "
                    % (self.url, cnt, self.num_retries) +
                    "Retrying in %d seconds" % sleeptime
                )
                time.sleep(sleeptime)
        except KeyboardInterrupt:
            self.keepalive.stop()
            raise
        except Exception as exc:
            raise exc

    def get_request_id(self):
        self._request_id += 1
        return self._request_id

    """ RPC Calls
    """
    def rpcexec(self, payload):
        """ Execute a call by sending the payload

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON format
            :raises RPCError: if the server returns an error
        """
        log.debug(json.dumps(payload))
        self.ws.send(json.dumps(payload, ensure_ascii=False).encode('utf8'))

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments
        """
        if name in self.__events__:
            return getattr(self.events, name)

        def method(*args, **kwargs):

            # Sepcify the api to talk to
            if "api_id" not in kwargs:
                if ("api" in kwargs):
                    if (kwargs["api"] in self.api_id and
                            self.api_id[kwargs["api"]]):
                        api_id = self.api_id[kwargs["api"]]
                    else:
                        raise ValueError(
                            "Unknown API! "
                            "Verify that you have registered to %s"
                            % kwargs["api"]
                        )
                else:
                    api_id = 0
            else:
                api_id = kwargs["api_id"]

            # let's be able to define the num_retries per query
            self.num_retries = kwargs.get("num_retries", self.num_retries)

            query = {"method": "call",
                     "params": [api_id, name, list(args)],
                     "jsonrpc": "2.0",
                     "id": self.get_request_id()}
            r = self.rpcexec(query)
            return r
        return method
