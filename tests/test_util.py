from unittest import IsolatedAsyncioTestCase
from unittest.mock import ANY, patch

import aiohttp
from yarl import URL

from util import on_request_end, on_request_start


class TestUtil(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)
        self.client = aiohttp.ClientSession(
            trace_configs=[trace_config],
        )

    async def asyncTearDown(self):
        await self.client.close()

    async def test_trace_config(self):
        with patch("util.logger.info") as mock_logging:
            await self.client.get("https://example.com")
            mock_logging.assert_any_call(
                "making %s request to %s", "GET", URL("https://example.com")
            )

            mock_logging.assert_any_call(
                "%s request to %s completed with status %s and data %s",
                "GET",
                URL("https://example.com"),
                200,
                ANY,
            )
