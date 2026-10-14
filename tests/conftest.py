"""Compatibility for aioresponses with aiohttp 3.14 and later."""

from types import SimpleNamespace

from aioresponses import core


class _AioresponsesClientResponse(core.ClientResponse):
    """Supply the stream writer required by newer aiohttp response objects."""

    def __init__(self, *args, stream_writer=None, **kwargs):
        if stream_writer is None:
            stream_writer = SimpleNamespace(output_size=0)
        super().__init__(*args, stream_writer=stream_writer, **kwargs)


# aioresponses constructs its own ClientResponse without this newer argument.
core.ClientResponse = _AioresponsesClientResponse
