# -*- coding: utf-8 -*-
import sys
import click
import time
import json

from grapheneapi.grapheneapi import GrapheneAPI

from bitshares.utils import formatTimeFromNow
from bitshares.genesisbalance import GenesisBalances
from bitshares.account import Account
from bitshares.amount import Amount
from bitshares.asset import Asset
from bitshares.proposal import Proposals
from bitshares.witness import Witness
from bitshares.blockchain import Blockchain

from bitshares import BitShares

from getpass import getpass

from pprint import pprint
from bitshares.instance import set_shared_blockchain_instance
from bitsharesbase.account import PasswordKey
from bitsharesbase import operations


connection = {
    "blocking": True,
    "nobroadcast": False,
    "num_retries": 1,
    #"node": ["wss://node.mvsdna.com"],
    "node": ["ws://localhost:8090"],
    "keys": [
        # udrur
        "5JEVg45P9ySbo4ZVuqfCBjydEi11C7n7z9PhqZAwwL8effcfEvU",  # initial balance
        "5JBtkKThCStcYZwBJhQEys1nc7e44F4giZCdLj3FyQWWAxESteB",  # foundation active
        "5JxNuvALBwigV29bnGd969sCsTwiuExs6pgdrnvvzs6PTvCiB9n",  # foundation owner
        "5JyhVvLVBo7ujoce5wHpCEWsnjVsmrmBHP8UK4Qy8pEYqXK6ptD",  # faucet
        "5KWNLXftSvmUaxmtfHPrwpD39654H3TwwaUkenpBNoLJsSvHPtW",  # init0 owner
    ]
}

blockchain = BitShares(
    **connection
)

set_shared_blockchain_instance(blockchain)


def sleep(t: int) -> None:
    click.echo(" - Going to sleep for {}s".format(t))
    time.sleep(int(t))


@click.group()
def main():
    pass


@main.command()
def info():
    click.echo(dict(Account("1.2.6")))


@main.command()
def listaccounts():
    click.echo(blockchain.wallet.getAccounts())


@main.command()
@click.argument("ids", required=False, nargs=-1)
def claim(ids):
    """ 2 - Claim genesis stake
    """
    _claim(ids)


def _claim(ids):
    # Claim genesis stake
    click.echo(" - Claiming Genesis Stake")
    p = GenesisBalances()
    if not ids:
        [click.echo(x) for x in p]
        return
    try:
        for x in p:
            if x["id"] in ids:
                click.echo(x.claim(account="foundation"))
        click.echo("Claimed!")
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))


@main.command()
def keys():
    password = "RYzJFo7uXPPoRtew"  # P5JNdP5NtnuaispDGX4gUdx6WkEXYLCrkvKYm6dH7mbXgX76VzLz
    keys = dict(
        active_key=str(PasswordKey("faucet", password, role="active").get_private_key()),
        owner_key=str(PasswordKey("faucet", password, role="owner").get_private_key()),
        memo_key=str(PasswordKey("faucet", password, role="memo").get_private_key())
    )
    click.echo(keys)


@main.command()
@click.argument("accounts", nargs=-1)
def accounts(accounts):
    """ 3 - create accounts
    """
    _accounts = [
        {
            "name": "faucet",
            "password": "RYzJFo7uXPPoRtew",
            "registrar": "foundation"
        },
        {
            "name": "debug",
            "password": "P5JNdP5NtnuaispDGX4gUdx6WkEXYLCrkvKYm6dH7mbXgX76VzLz"
        }
    ]
    for account in _accounts:
        if accounts is not None and account["name"] not in accounts:
            continue
        click.echo(" - Creating account {}".format(account["name"]))
        try:
            click.echo(
                blockchain.create_account(
                    account["name"], registrar=account.get("registrar", "faucet"), password=account["password"]
                )
            )
        except Exception as e:
            click.echo(click.style(str(e), fg="red"))


@main.command()
def upgrade():
    """ Upgrade accounts
    """
    accounts = ["faucet"]
    for account in accounts:
        click.echo(" - Upgrading account {}".format(account))
        try:
            click.echo(Account(account).upgrade())
        except Exception as e:
            click.echo(click.style(str(e), fg="red"))


@main.command()
@click.argument("account")
@click.argument("reward_percent")
def createwitness(
        account,
        reward_percent
):
    """ Upgrade accounts
    """
    click.echo(" - Creating witness for {}".format(account))
    try:
        click.echo("")
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))


@main.command()
@click.argument("account")
@click.argument("reward_percent")
def updatewitness(
    account,
    reward_percent
):
    GRAPHENE_1_PERCENT = 100

    witness = Witness(account)
    account = witness.account
    op = operations.Witness_update(
        **{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "prefix": blockchain.prefix,
            "witness": witness["id"],
            "witness_account": account["id"],
            "block_producer_reward_pct": int(reward_percent) * GRAPHENE_1_PERCENT
        }
    )
    return blockchain.finalizeOp(op, account["name"], "active")


@main.command()
def fund():
    """ Fund accounts
    """
    accounts = [
        "init0",
        "init1",
        "init2",
        "init3",
        "init4",
        "init5",
        "init6",
        "init7",
        "init8",
        "init9",
        "init10",
        "witness-account",
        "faucet"
    ]
    for account in accounts:
        click.echo(" - Transferring core token to account {}".format(account))
        try:
            click.echo(blockchain.transfer(account, 1000000, "DNA", account="foundation"))
        except Exception as e:
            click.echo(click.style(str(e), fg="red"))


@main.command()
@click.argument("accounts", nargs=-1)
def vote(accounts):
    """ 6 - Vote
    """
    _vote(accounts)


def _vote(accounts=None):
    if not accounts:
        accounts = [
            "init0",
            "init1",
            "init2",
            "init3",
            "init4",
            "init5",
            "init6",
            "init7",
            "init8",
            "init9",
            "init10",
        ]
    try:
        click.echo(blockchain.approvewitness(accounts, account="foundation"))
        click.echo("Voted!")
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))


@main.command()
def setupvesting():
    _setupvesting()


def _setupvesting():
    creator = Account("foundation")
    owner = Account("init0")
    amount = Amount("10000000 DNA")

    op = operations.Vesting_balance_create(
        **{
            "fee": {"amount": 0, "asset_id": "1.3.0"},
            "creator": creator["id"],
            "owner": owner["id"],
            "amount": amount.json(),
            "policy": [3, {"duration": 60 * 60 * 24 * 365}],
            "extensions": [],
        }
    )

    try:
        click.echo(blockchain.finalizeOp(op, creator, "active"))
        click.echo("Vested!")
    except Exception as e:
        click.echo(click.style(str(e), fg="red"))


@main.command()
def fixer():
    # claim
    _claim("1.15.0")

    _setupvesting()

    _vote()


if __name__ == "__main__":
    main()
