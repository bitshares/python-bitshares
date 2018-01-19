import re
import time
from datetime import datetime
from .exceptions import ObjectNotInProposalBuffer

timeFormat = '%Y-%m-%dT%H:%M:%S'


def formatTime(t):
    """ Properly Format Time for permlinks
    """
    if isinstance(t, float):
        return datetime.utcfromtimestamp(t).strftime(timeFormat)
    if isinstance(t, datetime):
        return t.strftime(timeFormat)


def formatTimeString(t):
    """ Properly Format Time for permlinks
    """
    return datetime.strptime(t, timeFormat)


def formatTimeFromNow(secs=0):
    """ Properly Format Time that is `x` seconds in the future

        :param int secs: Seconds to go in the future (`x>0`) or the
                         past (`x<0`)
        :return: Properly formated time for Graphene (`%Y-%m-%dT%H:%M:%S`)
        :rtype: str

    """
    return datetime.utcfromtimestamp(
        time.time() + int(secs)).strftime(timeFormat)


def parse_time(block_time):
    """Take a string representation of time from the blockchain, and parse it
       into datetime object.
    """
    return datetime.strptime(block_time, timeFormat)


def assets_from_string(text):
    """Correctly split a string containing an asset pair.

    Splits the string into two assets with the separator being on of the
    following: ``:``, ``/``, or ``-``.
    """
    return re.split(r'[\-:/]', text)

  
def test_proposal_in_buffer(buf, operation_name, id):
    from .transactionbuilder import ProposalBuilder
    from peerplaysbase.operationids import operations
    assert isinstance(buf, ProposalBuilder)

    operationid = operations.get(operation_name)
    _, _, j = id.split(".")

    ops = buf.list_operations()
    if (len(ops) <= int(j)):
        raise ObjectNotInProposalBuffer(
            "{} with id {} not found".format(
                operation_name,
                id
            )
        )
    op = ops[int(j)].json()
    if op[0] != operationid:
        raise ObjectNotInProposalBuffer(
            "{} with id {} not found".format(
                operation_name,
                id
            )
        )
