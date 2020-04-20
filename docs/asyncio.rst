Asyncio support
===============

The library has full support of asyncio, though you need to be aware it has some limitations.

Example
-------

A very basic example:

.. code-block:: python

    import asyncio

    from bitshares.aio import BitShares
    from bitshares.aio.instance import set_shared_bitshares_instance


    async def info(loop, bitshares):
        await bitshares.connect()
        set_shared_bitshares_instance(bitshares)
        print(await bitshares.info())


    def main():
        loop = asyncio.get_event_loop()
        bitshares = BitShares(loop=loop)
        loop.run_until_complete(info(loop, bitshares))


    if __name__ == '__main__':
        main()

Instantiation of BitShares
--------------------------

To be able to perform calls, you need to explicitly run `await BitShares.connect()`. That is, creating of instance
object and actual network connection are separate operations in async version:

.. code-block:: python

    bitshares = BitShares(loop=loop)
    await bitshares.connect()

Limitations
-----------

* Most of the classes requires async init because during instantiation some API calls has to be performed:

.. code-block:: python

    await Amount('10 FOO')

* Several math operations are not available for :class:`bitshares.aio.Amount`, :class:`bitshares.aio.Price`
  objects. This includes multiplication, division etc. This limitation is due to unability to define python magic
  methods (``__mul__``, ``__div__``, etc) as async coroutines
* Most of properties are awaitables too:

.. code-block:: python

    asset = await Asset('CNY')
    await asset.max_market_fee


Subscriptions
-------------

In asyncio version subscription notifications are not handled in callback-based manner. Instead, they are available in
`self.notifications` queue which is :class:`asyncio.Queue`. You can use a single bitshares instance both for setting
subscriptions and performing other API calls.

Here is the example of how to subscribe and handle events:

.. code-block:: python

    market = await Market("TEST/USD")
    await bitshares.subscribe_to_market(market, event_id=4)

    while True:
        event = await bitshares.notifications.get()
        print(event)


Debugging
---------

To enable debugging on RPC level, you can raise loglevel on following loggers (don't forget to set formatter as well):

.. code-block:: python

    log = logging.getLogger("websockets")
    log.setLevel(logging.DEBUG)

    log = logging.getLogger("grapheneapi")
    log.setLevel(logging.DEBUG)

Tests
-----

Asyncio version has a dedicated testsuite which uses real API integration tests which are performed against local
bitshares-core testnet. Bitshares node is spawned automatically inside docker container. You don't need to setup
anything.

Before running tests you need to install dependencies via `pip intstall -r requirements-test.txt`

Run tests via `pytest -v tests/testnet/aio/`
