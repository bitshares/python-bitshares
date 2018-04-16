import time
from .block import Block
from .instance import BlockchainInstance
from bitsharesbase.operationids import getOperationNameForId


class Blockchain(object):
    """ This class allows to access the blockchain and read data
        from it

        :param bitshares.bitshares.BitShares blockchain_instance: BitShares
                 instance
        :param str mode: (default) Irreversible block (``irreversible``) or
                 actual head block (``head``)
        :param int max_block_wait_repetition: (default) 3 maximum wait time for
            next block ismax_block_wait_repetition * block_interval

        This class let's you deal with blockchain related data and methods.
    """
    def __init__(
        self,
        blockchain_instance=None,
        mode="irreversible",
        max_block_wait_repetition=None,
        *args,
        **kwargs
    ):
        BlockchainInstance.__init__(self, *args, **kwargs)

        if mode == "irreversible":
            self.mode = 'last_irreversible_block_num'
        elif mode == "head":
            self.mode = "head_block_number"
        else:
            raise ValueError("invalid value for 'mode'!")

        if max_block_wait_repetition:
            self.max_block_wait_repetition = max_block_wait_repetition
        else:
            self.max_block_wait_repetition = 3

    def is_irreversible_mode(self):
        return self.mode == 'last_irreversible_block_num'

    def info(self):
        """ This call returns the *dynamic global properties*
        """
        return self.blockchain.rpc.get_dynamic_global_properties()

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
        return self.blockchain.rpc.get_network()

    def get_chain_properties(self):
        """ Return chain properties
        """
        return self.blockchain.rpc.get_chain_properties()

    def config(self):
        """ Returns object 2.0.0
        """
        return self.blockchain.rpc.get_object("2.0.0")

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
        return Block(
            self.get_current_block_num(),
            blockchain_instance=self.blockchain
        )

    def block_time(self, block_num):
        """ Returns a datetime of the block with the given block
            number.

            :param int block_num: Block number
        """
        return Block(
            block_num,
            blockchain_instance=self.blockchain
        ).time()

    def block_timestamp(self, block_num):
        """ Returns the timestamp of the block with the given block
            number.

            :param int block_num: Block number
        """
        return int(Block(
            block_num,
            blockchain_instance=self.blockchain
        ).time().timestamp())

    def blocks(self, start=None, stop=None):
        """ Yields blocks starting from ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
             "head" (the last block) and "irreversible" (the block that is
             confirmed by 2/3 of all block producers and is thus irreversible)
        """
        # Let's find out how often blocks are generated!
        self.block_interval = self.chainParameters().get("block_interval")

        if not start:
            start = self.get_current_block_num()

        # We are going to loop indefinitely
        while True:

            # Get chain properies to identify the
            if stop:
                head_block = stop
            else:
                head_block = self.get_current_block_num()

            # Blocks from start until head block
            for blocknum in range(start, head_block + 1):
                # Get full block
                block = self.wait_for_and_get_block(blocknum)
                block.update({"block_num": blocknum})
                yield block
            # Set new start
            start = head_block + 1

            if stop and start > stop:
                # raise StopIteration
                return

            # Sleep for one block
            time.sleep(self.block_interval)

    def wait_for_and_get_block(self, block_number, blocks_waiting_for=None):
        """ Get the desired block from the chain, if the current head block is
            smaller (for both head and irreversible) then we wait, but a
            maxmimum of blocks_waiting_for * max_block_wait_repetition time
            before failure.

            :param int block_number: desired block number
            :param int blocks_waiting_for: (default) difference between
                block_number and current head how many blocks we are willing to
                wait, positive int
        """
        if not blocks_waiting_for:
            blocks_waiting_for = max(
                1, block_number - self.get_current_block_num())

        repetition = 0
        # can't return the block before the chain has reached it (support
        # future block_num)
        while self.get_current_block_num() < block_number:
            repetition += 1
            time.sleep(self.block_interval)
            if (
                repetition >
                blocks_waiting_for * self.max_block_wait_repetition
            ):
                raise Exception("Wait time for new block exceeded, aborting")
        # block has to be returned properly
        block = self.blockchain.rpc.get_block(block_number)
        repetition = 0
        while not block:
            repetition += 1
            time.sleep(self.block_interval)
            if repetition > self.max_block_wait_repetition:
                raise Exception("Wait time for new block exceeded, aborting")
            block = self.blockchain.rpc.get_block(block_number)
        return block

    def ops(self, start=None, stop=None, **kwargs):
        """ Yields all operations (including virtual operations) starting from
            ``start``.

            :param int start: Starting block
            :param int stop: Stop at this block
            :param str mode: We here have the choice between
             "head" (the last block) and "irreversible" (the block that is
             confirmed by 2/3 of all block producers and is thus irreversible)
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
                 * "irreversible": the block that is confirmed by 2/3 of all
                    block producers and is thus irreversible!

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
        """ Returns the transaction as seen by the blockchain after being
            included into a block

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
                if (
                    sorted(tx["signatures"]) ==
                    sorted(transaction["signatures"])
                ):
                    return tx
            if counter > limit:
                raise Exception(
                    "The operation has not been added after 10 blocks!")

    def get_all_accounts(self, start='', stop='', steps=1e3, **kwargs):
        """ Yields account names between start and stop.

            :param str start: Start at this account name
            :param str stop: Stop at this account name
            :param int steps: Obtain ``steps`` ret with a single call from RPC
        """
        lastname = start
        while True:
            ret = self.blockchain.rpc.lookup_accounts(lastname, steps)
            for account in ret:
                yield account[0]
                if account[0] == stop:
                    raise StopIteration
            if lastname == ret[-1][0]:
                raise StopIteration
            lastname = ret[-1][0]
            if len(ret) < steps:
                raise StopIteration
