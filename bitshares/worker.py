from .instance import BlockchainInstance
from .account import Account
from .exceptions import WorkerDoesNotExistsException
from .utils import formatTimeString
from .blockchainobject import BlockchainObject


class Worker(BlockchainObject):
    """ Read data about a worker in the chain

        :param str id: id of the worker
        :param bitshares blockchain_instance: BitShares() instance to use when
            accesing a RPC

    """
    type_id = 14

    def refresh(self):
        worker = self.blockchain.rpc.get_object(self.identifier)
        if not worker:
            raise WorkerDoesNotExistsException
        worker["work_end_date"] = formatTimeString(worker["work_end_date"])
        worker["work_begin_date"] = formatTimeString(worker["work_begin_date"])
        super(Worker, self).__init__(worker, blockchain_instance=self.blockchain)
        self.cached = True

    @property
    def account(self):
        return Account(
            self["worker_account"], blockchain_instance=self.blockchain)


class Workers(list):
    """ Obtain a list of workers for an account

        :param str account_name/id: Name/id of the account (optional)
        :param bitshares blockchain_instance: BitShares() instance to use when
            accesing a RPC
    """
    def __init__(self, account_name=None, **kwargs):
        BlockchainInstance.__init__(self, **kwargs)
        if account_name:
            account = Account(account_name, blockchain_instance=self.blockchain)
            self.workers = self.blockchain.rpc.get_workers_by_account(
                account["id"])
        else:
            self.workers = self.blockchain.rpc.get_all_workers()

        super(Workers, self).__init__(
            [
                Worker(x, lazy=True, blockchain_instance=self.blockchain)
                for x in self.workers
            ]
        )
