import json
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from aioresponses import aioresponses

from src.util.GoveeAPI import GoveeAPI


class TestGoveeAPI(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api_key = "test-api-key"
        self.govee = GoveeAPI(self.api_key)
        self.mock_aioresponse = aioresponses()
        self.mock_aioresponse.start()

        # Load test data from JSON file
        test_data_path = Path(__file__).parent / "test_data" / "govee_api.json"
        with open(test_data_path, "r") as f:
            self.test_data = json.load(f)

    async def asyncTearDown(self):
        await self.govee.client.close()
        self.mock_aioresponse.stop()

    async def test_get_devices(self):
        # Get response data from the loaded test data
        mock_response = self.test_data["get_devices"]

        # Mock the GET request
        self.mock_aioresponse.get(
            "https://openapi.api.govee.com/router/api/v1/user/devices",
            status=200,
            payload=mock_response,
        )

        # Call the method being tested
        result = await self.govee.get_devices()

        # Verify the results
        self.assertEqual(result, mock_response["data"])
