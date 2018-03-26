from transnet.instance import shared_transnet_instance
from .account import Account
from .exceptions import WorkerDoesNotExistsException
from .utils import formatTimeString
from .blockchainobject import BlockchainObject


class Worker(BlockchainObject):
    """ Read data about a worker in the chain

        :param str id: id of the worker
        :param transnet transnet_instance: Transnet() instance to use when
            accesing a RPC

    """
    type_id = 14

    def refresh(self):
        worker = self.transnet.rpc.get_object(self.identifier)
        if not worker:
            raise WorkerDoesNotExistsException
        worker["work_end_date"] = formatTimeString(worker["work_end_date"])
        worker["work_begin_date"] = formatTimeString(worker["work_begin_date"])
        super(Worker, self).__init__(worker, transnet_instance=self.transnet)
        self.cached = True

    @property
    def account(self):
        return Account(
            self["worker_account"], transnet_instance=self.transnet)


class Workers(list):
    """ Obtain a list of workers for an account

        :param str account_name/id: Name/id of the account (optional)
        :param transnet transnet_instance: Transnet() instance to use when
            accesing a RPC
    """
    def __init__(self, account_name=None, transnet_instance=None):
        self.transnet = transnet_instance or shared_transnet_instance()
        if account_name:
            account = Account(account_name, transnet_instance=self.transnet)
            self.workers = self.transnet.rpc.get_workers_by_account(
                account["id"])
        else:
            self.workers = self.transnet.rpc.get_all_workers()

        super(Workers, self).__init__(
            [
                Worker(x, lazy=True, transnet_instance=self.transnet)
                for x in self.workers
            ]
        )
