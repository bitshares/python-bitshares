from bitshares.asset import Asset
from bitshares import BitShares


# Mocker comes from pytest-mock, providing an easy way to have patched objects
# for the life of the test.
def test_calls(mocker):
    asset = Asset("USD", lazy=True, bitshares_instance=BitShares(offline=True))
    method = mocker.patch.object(Asset, 'get_call_orders')
    asset.calls
    method.assert_called_with(10)
