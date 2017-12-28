import time
from .block import Block
from bitshares.instance import shared_bitshares_instance
from .utils import parse_time
from bitsharesbase.operationids import operations, getOperationNameForId


class Blockchain(object):
    """ This class allows to access the blockchain and read data
        from it

        :param bitshares.bitshares.BitShares bitshares_instance: BitShares instance
        :param str mode: (default) Irreversible block (``irreversible``) or actual head block (``head``)

        This class let's you deal with blockchain related data and methods.
    """
    def __init__(
        self,
        bitshares_instance=None,
        mode="irreversible"
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()

        if mode == "irreversible":
            self.mode = 'last_irreversible_block_num'
        elif mode == "head":
            self.mode = "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.bitshares.rpc.get_dynamic_global_properties()

    def chainParameters(self):
        """ The blockchain parameters, such as fees, and committee-controlled
            parameters are returned here
        """
        return self.config()["parameters"]

    def get_network(self):
        """ Identify the network

            :returns: Network parameters
            :rtype: dict
        """
        return self.bitshares.rpc.get_network()

    def get_chain_properties(self):
        """ Return chain properties
        """
        return self.bitshares.rpc.get_chain_properties()

    def config(self):
        """ Returns object 2.0.0
        """
        return self.bitshares.rpc.get_object("2.0.0")

    def get_current_block_num(self):
        """ This call returns the current block

            .. note:: The block number returned depends on the ``mode`` used
                      when instanciating from this class.
        """
        return self.info().get(self.mode)

    def get_current_block(self):
        """ This call returns the current block

            .. note:: The block number returned depends on the ``mode`` used
                      when instanciating from this class.
        """
        return Block(self.get_current_block_num())

    def block_time(self, block_num):
        """ Returns a datetime of the block with the given block
            number.

            :param int block_num: Block number
        """
        return Block(block_num).time()

    def block_timestamp(self, block_num):
        """ Returns the timestamp of the block with the given block
            number.

            :param int block_num: Block number
        """
        return int(Block(block_num).time().timestamp())

    def blocks(self, start=None, stop=None):
        """ Yields blocks starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
        """
        # Let's find out how often blocks are generated!
        block_interval = self.chainParameters().get("block_interval")

        if not start:
            start = self.get_current_block_num()

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            head_block = self.get_current_block_num()

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                block = self.bitshares.rpc.get_block(blocknum)
                block.update({"block_num": blocknum})
                yield block
            # Set new start
            start = head_block + 1

            if stop and start > stop:
                raise StopIteration

            # Sleep for one block
            time.sleep(block_interval)

    def ops(self, start=None, stop=None, **kwargs):
        """ Yields all operations (including virtual operations) starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!
            :param bool only_virtual_ops: Only yield virtual operations

            This call returns a list that only carries one operation and
            its type!
        """

        for block in self.blocks(start=start, stop=stop, **kwargs):
            for tx in block["transactions"]:
                for op in tx["operations"]:
                    # Replace opid by op name
                    op[0] = getOperationNameForId(op[0])
                    yield {
                        "block_num": block["block_num"],
                        "op": op,
                        "timestamp": block["timestamp"]
                    }

    def stream(self, opNames=[], *args, **kwargs):
        """ Yield specific operations (e.g. comments) only

            :param array opNames: List of operations to filter for
            :param int start: Start at this block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
                 * "head": the last block
                 * "irreversible": the block that is confirmed by 2/3 of all block producers and is thus irreversible!

            The dict output is formated such that ``type`` caries the
            operation type, timestamp and block_num are taken from the
            block the operation was stored in and the other key depend
            on the actualy operation.
        """
        for op in self.ops(**kwargs):
            if not opNames or op["op"][0] in opNames:
                r = {
                    "type": op["op"][0],
                    "timestamp": op.get("timestamp"),
                    "block_num": op.get("block_num"),
                }
                r.update(op["op"][1])
                yield r

    def awaitTxConfirmation(self, transaction, limit=10):
        """ Returns the transaction as seen by the blockchain after being included into a block

            .. note:: If you want instant confirmation, you need to instantiate
                      class:`bitshares.blockchain.Blockchain` with
                      ``mode="head"``, otherwise, the call will wait until
                      confirmed in an irreversible block.

            .. note:: This method returns once the blockchain has included a
                      transaction with the **same signature**. Even though the
                      signature is not usually used to identify a transaction,
                      it still cannot be forfeited and is derived from the
                      transaction contented and thus identifies a transaction
                      uniquely.
        """
        counter = 10
        for block in self.blocks():
            counter += 1
            for tx in block["transactions"]:
                if sorted(tx["signatures"]) == sorted(transaction["signatures"]):
                    return tx
            if counter > limit:
                raise Exception("The operation has not been added after 10 blocks!")

    def get_all_accounts(self, start='', stop='', steps=1e3, **kwargs):
        """ Yields account names between start and stop.

            :param str start: Start at this account name
            :param str stop: Stop at this account name
            :param int steps: Obtain ``steps`` ret with a single call from RPC
        """
        lastname = start
        while True:
            ret = self.bitshares.rpc.lookup_accounts(lastname, steps)
            for account in ret:
                yield account[0]
                if account[0] == stop:
                    raise StopIteration
            if lastname == ret[-1][0]:
                raise StopIteration
            lastname = ret[-1][0]
            if len(ret) < steps:
                raise StopIteration
