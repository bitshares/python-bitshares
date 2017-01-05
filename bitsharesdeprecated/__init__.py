import warnings
warnings.warn(
    "The %s module will be deprecated and replaced soon" % __name__,
    DeprecationWarning
)

__all__ = [
    'client',
    "websocket",
    "websocketprotocol"
]
