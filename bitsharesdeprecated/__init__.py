import warnings
warnings.warn(
    "[DeprecationWarning] The % module will be deprecated and replaced soon" % __name__
)

__all__ = [
    'client',
    "websocket",
    "websocketprotocol"
]
