import re
from grapheneapi.graphenewsrpc import GrapheneWebsocketRPC
from grapheneapi.graphenehttprpc import GrapheneHTTPRPC
from bitsharesbase.chains import known_chains
from . import exceptions
import logging
log = logging.getLogger(__name__)


class BitSharesNodeRPC(GrapheneWebsocketRPC, GrapheneHTTPRPC):

    def __init__(self,
                 urls,
                 user="",
                 password="",
                 **kwargs):
        if isinstance(urls, str):
            self._urls = re.split(r",|;", urls)
        elif isinstance(urls, (list, tuple, set)):
            self._urls = urls
        else:
            raise exceptions.InvalidEndpointUrl
        self.rpc.__init__(self, self._urls, **kwargs)
        self.chain_params = self.get_network()

    def next(self):
        """ Iterate over to the next API node an reconnect
        """
        self.rpc.next()

    @property
    def rpc(self):
        first_url = self._urls[0]

        if first_url[:2] == "ws":
            # Websocket connection
            return GrapheneWebsocketRPC
        else:
            # RPC/HTTP connection
            return GrapheneHTTPRPC

    def rpcexec(self, payload):
        """ Execute a call by sending the payload.
            It makes use of the GrapheneRPC library.
            In here, we mostly deal with BitShares specific error handling

            :param json payload: Payload data
            :raises ValueError: if the server does not respond in proper JSON
                                format
            :raises RPCError: if the server returns an error
        """
        try:
            # Forward call to GrapheneWebsocketRPC and catch+evaluate errors
            return self.rpc.rpcexec(self, payload)
        except exceptions.RPCError as e:
            msg = exceptions.decodeRPCErrorMsg(e).strip()
            if msg == "missing required active authority":
                raise exceptions.MissingRequiredActiveAuthority
            elif re.match("current_account_itr == acnt_indx.indices().get<by_name>().end()", msg):
                raise exceptions.AccountCouldntBeFoundException(msg)
            elif re.match("Assert Exception: is_valid_name( name )", msg):
                raise exceptions.InvalidAccountNameException(msg)
            elif re.match("^no method with name.*", msg):
                raise exceptions.NoMethodWithName(msg)
            elif msg:
                raise exceptions.UnhandledRPCError(msg)
            else:
                raise e
        except Exception as e:
            raise e

    def get_account(self, name, **kwargs):
        """ Get full account details from account name or id

            :param str name: Account name or account id
        """
        if len(name.split(".")) == 3:
            return self.get_objects([name])[0]
        else:
            return self.get_account_by_name(name, **kwargs)

    def get_asset(self, name, **kwargs):
        """ Get full asset from name of id

            :param str name: Symbol name or asset id (e.g. 1.3.0)
        """
        if len(name.split(".")) == 3:
            return self.get_objects([name], **kwargs)[0]
        else:
            return self.lookup_asset_symbols([name], **kwargs)[0]

    def get_object(self, o, **kwargs):
        """ Get object with id ``o``

            :param str o: Full object id
        """
        return self.get_objects([o], **kwargs)[0]

    def get_network(self):
        """ Identify the connected network. This call returns a
            dictionary with keys chain_id, core_symbol and prefix
        """
        props = self.get_chain_properties()
        chain_id = props["chain_id"]
        for k, v in known_chains.items():
            if v["chain_id"] == chain_id:
                return v
        raise Exception("Connecting to unknown network!")

    def __getattr__(self, name):
        """ Map all methods to RPC calls and pass through the arguments.
            It makes use of the GrapheneRPC library.
        """
        return self.rpc.__getattr__(self, name)
