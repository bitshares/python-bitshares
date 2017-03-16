from events import Events
from bitsharesapi.websocket import BitSharesWebsocket
from bitshares.instance import shared_bitshares_instance
from bitshares.market import Market
from bitshares.price import Order, FilledOrder
from bitshares.account import Account, AccountUpdate


class Notify(Events):

    __events__ = [
        'on_tx',
        'on_object',
        'on_block',
        'on_account',
        'on_market',
    ]

    def __init__(
        self,
        *args,
        bitshares_instance=None,
        accounts=[],
        markets=[],
        objects=[],
        on_tx=None,
        on_object=None,
        on_block=None,
        on_account=None,
        on_market=None,
        **kwargs,
    ):
        Events.__init__(self, *args, **kwargs)
        self.events = Events()
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        market_ids = []
        for market_name in markets:
            market = Market(
                market_name,
                bitshares_instance=self.bitshares
            )
            market_ids.append([
                market["base"]["id"],
                market["quote"]["id"],
            ])

        account_ids = []
        for account_name in accounts:
            account = Account(
                account_name,
                bitshares_instance=self.bitshares
            )
            account_ids.append(account["id"])

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

        self.websocket = BitSharesWebsocket(
            urls=self.bitshares.rpc.urls,
            user=self.bitshares.rpc.user,
            password=self.bitshares.rpc.password,
            accounts=account_ids,
            markets=market_ids,
            objects=objects,
            on_tx=on_tx,
            on_object=on_object,
            on_block=on_block,
            on_account=self._process_account,
            on_market=self._process_market,
        )

    def _process_market(self, ids):
        for id in ids:
            if isinstance(id, str):
                # Single order has been placed
                self.on_market(Order(id))
            else:
                # Orders have been matched
                for p in id:
                    if p[1]:
                        self.on_market(FilledOrder(p[1]))

    def _process_account(self, message):
        self.on_account(AccountUpdate(message))

    def listen(self):
        self.websocket.run_forever()
