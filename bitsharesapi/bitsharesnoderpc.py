import re

from bitsharesbase.chains import known_chains
from grapheneapi.api import Api as Original_Api

from . import exceptions


class Api(Original_Api):
    def post_process_exception(self, e):
        msg = exceptions.decodeRPCErrorMsg(e).strip()
        if msg == "missing required active authority":
            raise exceptions.MissingRequiredActiveAuthority
        elif re.match(
            "current_account_itr == acnt_indx.indices().get<by_name>().end()", msg
        ):
            raise exceptions.AccountCouldntBeFoundException(msg)
        elif re.match("Assert Exception: is_valid_name( name )", msg):
            raise exceptions.InvalidAccountNameException(msg)
        elif re.match("^no method with name.*", msg):
            raise exceptions.NoMethodWithName(msg)
        elif msg:
            raise exceptions.UnhandledRPCError(msg)
        else:
            raise e


class BitSharesNodeRPC(Api):
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
