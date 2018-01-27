from bitshares.instance import shared_bitshares_instance
from .account import Account
from .exceptions import WorkerDoesNotExistsException
from .utils import formatTimeString
from .blockchainobject import BlockchainObject


class Worker(BlockchainObject):
    """ Read data about a worker in the chain

        :param str id: id of the worker
        :param bitshares bitshares_instance: BitShares() instance to use when
            accesing a RPC

    """
    type_id = 14

    def refresh(self):
        worker = self.bitshares.rpc.get_object(self.identifier)
        if not worker:
            raise WorkerDoesNotExistsException
        worker["work_end_date"] = formatTimeString(worker["work_end_date"])
        worker["work_begin_date"] = formatTimeString(worker["work_begin_date"])
        super(Worker, self).__init__(worker, bitshares_instance=self.bitshares)
        self.cached = True

    @property
    def account(self):
        return Account(
            self["worker_account"], bitshares_instance=self.bitshares)


class Workers(list):
    """ Obtain a list of workers for an account

        :param str account_name/id: Name/id of the account (optional)
        :param bitshares bitshares_instance: BitShares() instance to use when
            accesing a RPC
    """
    def __init__(self, account_name=None, bitshares_instance=None):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        if account_name:
            account = Account(account_name, bitshares_instance=self.bitshares)
            self.workers = self.bitshares.rpc.get_workers_by_account(
                account["id"])
        else:
            self.workers = self.bitshares.rpc.get_all_workers()

        super(Workers, self).__init__(
            [
                Worker(x, lazy=True, bitshares_instance=self.bitshares)
                for x in self.workers
            ]
        )
