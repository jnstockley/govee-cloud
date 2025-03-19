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

    async def test_get_devices_bad_api_key(self):
        self.mock_aioresponse.get(
            "https://openapi.api.govee.com/router/api/v1/user/devices", status=401
        )

        with self.assertRaises(RuntimeError):
            await self.govee.get_devices()

    async def test_get_devices_rate_limited(self):
        self.mock_aioresponse.get(
            "https://openapi.api.govee.com/router/api/v1/user/devices", status=429
        )

        with self.assertRaises(RuntimeError):
            await self.govee.get_devices()

    async def test_get_device_state(self):
        sku = "H7143"
        device = "52:8B:D4:AD:FC:45:5D:FE"
        uuid = "98e662be-9837-439f-833e-83b5152142f5"

        mock_response = self.test_data["get_device_state"]

        # Mock the GET request
        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/state",
            status=200,
            payload=mock_response,
        )

        # Call the method being tested
        result = await self.govee.get_device_state(sku, device, request_id=uuid)

        # Verify the results
        self.assertEqual(result, mock_response["payload"])

    async def test_get_device_state_invalid_request_id(self):
        sku = "H7143"
        device = "52:8B:D4:AD:FC:45:5D:FE"
        uuid = "invalid-request-id"

        mock_response = self.test_data["get_device_state"]

        # Mock the GET request
        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/state",
            status=200,
            payload=mock_response,
        )

        with self.assertRaises(RuntimeError):
            await self.govee.get_device_state(sku, device, request_id=uuid)

    async def test_get_device_state_bad_api_key(self):
        sku = "H7143"
        device = "52:8B:D4:AD:FC:45:5D:FE"
        uuid = "98e662be-9837-439f-833e-83b5152142f5"

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/state", status=401
        )

        with self.assertRaises(RuntimeError):
            await self.govee.get_device_state(sku, device, request_id=uuid)

    async def test_get_device_state_rate_limited(self):
        sku = "H7143"
        device = "52:8B:D4:AD:FC:45:5D:FE"
        uuid = "98e662be-9837-439f-833e-83b5152142f5"

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/state", status=429
        )

        with self.assertRaises(RuntimeError):
            await self.govee.get_device_state(sku, device, request_id=uuid)
