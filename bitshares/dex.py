# -*- coding: utf-8 -*-
# from .storage import config
from bitsharesbase import operations

from .account import Account
from .amount import Amount
from .asset import Asset
from .instance import BlockchainInstance
from .price import Price


class Dex(BlockchainInstance):
    """ This class simplifies interactions with the decentralized exchange.

        :param bitshares.bitshares.BitShares blockchain_instance: BitShares instance

        .. note:: The methods of this class only deal with a single asset (at
                  most). If you are looking to deal with orders for trading,
                  please use :class:`bitshares.market.Market`.

    """

    def __init__(self, *args, **kwargs):
        BlockchainInstance.__init__(self, *args, **kwargs)

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
        from bitsharesbase.operations import operations

        r = {}
        obj, base = self.blockchain.rpc.get_objects(["2.0.0", "1.3.0"])
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

    def list_debt_positions(self, account=None):
        """ List Call Positions (borrowed assets and amounts)

            :return: Struct of assets with amounts and call price
            :rtype: dict

            **Example**:

            .. code-block: js

                {'USD': {'collateral': '865893.75000',
                         'collateral_asset': 'BTS',
                         'debt': 120.00000}

        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, blockchain_instance=self.blockchain)

        r = {}
        for debt in account.get("call_orders"):
            base = Asset(
                debt["call_price"]["base"]["asset_id"],
                full=True,
                blockchain_instance=self.blockchain,
            )
            quote = Asset(
                debt["call_price"]["quote"]["asset_id"],
                full=True,
                blockchain_instance=self.blockchain,
            )
            if not quote.is_bitasset:
                continue
            quote.ensure_full()
            bitasset = quote["bitasset_data"]
            settlement_price = Price(
                bitasset["current_feed"]["settlement_price"],
                blockchain_instance=self.blockchain,
            )
            if not settlement_price:
                continue
            call_price = Price(debt["call_price"], blockchain_instance=self.blockchain)
            collateral_amount = Amount({"amount": debt["collateral"], "asset": base})
            debt_amount = Amount({"amount": debt["debt"], "asset": quote})
            r[quote["symbol"]] = {
                "collateral": collateral_amount,
                "debt": debt_amount,
                "call_price": call_price,
                "settlement_price": settlement_price,
                "ratio": float(collateral_amount)
                / float(debt_amount)
                * float(settlement_price),
            }
        return r

    def close_debt_position(self, symbol, account=None):
        """ Close a debt position and reclaim the collateral

            :param str symbol: Symbol to close debt position for
            :raises ValueError: if symbol has no open call position
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, blockchain_instance=self.blockchain)
        debts = self.list_debt_positions(account)
        if symbol not in debts:
            raise ValueError("No call position open for %s" % symbol)
        debt = debts[symbol]
        asset = debt["debt"]["asset"]
        collateral_asset = debt["collateral"]["asset"]
        op = operations.Call_order_update(
            **{
                "fee": {"amount": 0, "asset_id": "1.3.0"},
                "delta_debt": {
                    "amount": int(-float(debt["debt"]) * 10 ** asset["precision"]),
                    "asset_id": asset["id"],
                },
                "delta_collateral": {
                    "amount": int(
                        -float(debt["collateral"]) * 10 ** collateral_asset["precision"]
                    ),
                    "asset_id": collateral_asset["id"],
                },
                "funding_account": account["id"],
                "extensions": [],
            }
        )
        return self.blockchain.finalizeOp(op, account["name"], "active")

    def adjust_debt(
        self,
        delta,
        new_collateral_ratio=None,
        account=None,
        target_collateral_ratio=None,
    ):
        """ Adjust the amount of debt for an asset

            :param Amount delta: Delta amount of the debt (-10 means reduce
                debt by 10, +10 means borrow another 10)
                :param float new_collateral_ratio: collateral ratio to maintain
                (optional, by default tries to maintain old ratio)
            :param float target_collateral_ratio: Tag the call order so that in
                case of margin call, only enough debt is covered to get back to
                this ratio
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance
                collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, blockchain_instance=self.blockchain)

        # We sell quote and pay with base
        symbol = delta["symbol"]
        asset = Asset(symbol, full=True, blockchain_instance=self.blockchain)
        if not asset.is_bitasset:
            raise ValueError("%s is not a bitasset!" % symbol)
        bitasset = asset["bitasset_data"]

        # Check minimum collateral ratio
        backing_asset_id = bitasset["options"]["short_backing_asset"]
        current_debts = self.list_debt_positions(account)
        if not new_collateral_ratio and symbol not in current_debts:
            new_collateral_ratio = (
                bitasset["current_feed"]["maintenance_collateral_ratio"] / 1000
            )
        elif not new_collateral_ratio and symbol in current_debts:
            new_collateral_ratio = current_debts[symbol]["ratio"]

        # Derive Amount of Collateral
        collateral_asset = Asset(backing_asset_id, blockchain_instance=self.blockchain)
        settlement_price = Price(
            bitasset["current_feed"]["settlement_price"],
            blockchain_instance=self.blockchain,
        )

        if symbol in current_debts:
            amount_of_collateral = (
                (float(current_debts[symbol]["debt"]) + float(delta["amount"]))
                * new_collateral_ratio
                / float(settlement_price)
            )
            amount_of_collateral -= float(current_debts[symbol]["collateral"])
        else:
            amount_of_collateral = (
                float(delta["amount"]) * new_collateral_ratio / float(settlement_price)
            )

        # Verify that enough funds are available
        fundsNeeded = amount_of_collateral + float(
            self.returnFees()["call_order_update"]["fee"]
        )
        fundsHave = account.balance(collateral_asset["symbol"]) or 0
        if fundsHave <= fundsNeeded:
            raise ValueError(
                "Not enough funds available. Need %f %s, but only %f %s are available"
                % (
                    fundsNeeded,
                    collateral_asset["symbol"],
                    fundsHave,
                    collateral_asset["symbol"],
                )
            )

        payload = {
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "delta_debt": {
                "amount": int(float(delta) * 10 ** asset["precision"]),
                "asset_id": asset["id"],
            },
            "delta_collateral": {
                "amount": int(
                    float(amount_of_collateral) * 10 ** collateral_asset["precision"]
                ),
                "asset_id": collateral_asset["id"],
            },
            "funding_account": account["id"],
            "extensions": {},
        }
        # Extension
        if target_collateral_ratio:
            payload["extensions"].update(
                dict(target_collateral_ratio=int(target_collateral_ratio * 100))
            )

        op = operations.Call_order_update(**payload)
        return self.blockchain.finalizeOp(op, account["name"], "active")

    def adjust_collateral_ratio(
        self, symbol, new_collateral_ratio, account=None, target_collateral_ratio=None
    ):
        """ Adjust the collataral ratio of a debt position

            :param Asset amount: Amount to borrow (denoted in 'asset')
            :param float new_collateral_ratio: desired collateral ratio
            :param float target_collateral_ratio: Tag the call order so that in
                case of margin call, only enough debt is covered to get back to
                this ratio
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available
        """
        if not account:
            if "default_account" in self.blockchain.config:
                account = self.blockchain.config["default_account"]
        if not account:
            raise ValueError("You need to provide an account")
        account = Account(account, full=True, blockchain_instance=self.blockchain)
        current_debts = self.list_debt_positions(account)
        if symbol not in current_debts:
            raise ValueError(
                "No Call position available to adjust! Please borrow first!"
            )
        return self.adjust_debt(
            Amount(0, symbol),
            new_collateral_ratio,
            account,
            target_collateral_ratio=target_collateral_ratio,
        )

    def borrow(
        self, amount, collateral_ratio=None, account=None, target_collateral_ratio=None
    ):
        """ Borrow bitassets/smartcoins from the network by putting up
            collateral in a CFD at a given collateral ratio.

            :param float amount: Amount to borrow (denoted in 'asset')
            :param float collateral_ratio: Collateral ratio to borrow at
            :param float target_collateral_ratio: Tag the call order so that in
                case of margin call, only enough debt is covered to get back to
                this ratio
            :raises ValueError: if symbol is not a bitasset
            :raises ValueError: if collateral ratio is smaller than maintenance collateral ratio
            :raises ValueError: if required amounts of collateral are not available

        """
        return self.adjust_debt(
            amount,
            collateral_ratio,
            account,
            target_collateral_ratio=target_collateral_ratio,
        )
