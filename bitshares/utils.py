import time
from datetime import datetime

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
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime(timeFormat)


def parse_time(block_time):
    """Take a string representation of time from the blockchain, and parse it into datetime object.
    """
    return datetime.strptime(block_time, timeFormat)
