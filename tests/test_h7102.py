import json
from pathlib import Path
from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch

from aioresponses import aioresponses

from devices.fan.h7102 import H7102
from util.govee_api import GoveeAPI


class TestH7102(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.api_key = "test-api-key"
        self.govee = GoveeAPI(self.api_key, ignore_request_id=True)
        self.device_id = "test-device-id"
        self.device = H7102(self.device_id)
        self.mock_aioresponse = aioresponses()
        self.mock_aioresponse.start()

        # Load test data from JSON file
        test_data_path = Path(__file__).parent / "test_data" / "h7102.json"
        with open(test_data_path, "r") as f:
            self.test_data = json.load(f)

    async def asyncTearDown(self):
        await self.govee.client.close()
        self.mock_aioresponse.stop()

    async def test_power_switch(self):
        mock_response = self.test_data["power_switch_response"]

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.turn_on(self.govee)
        self.assertTrue(self.device.power_switch)

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.turn_off(self.govee)
        self.assertFalse(self.device.power_switch)

    async def test_oscillation(self):
        mock_response = self.test_data["oscillation_response"]

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.toggle_oscillation(self.govee, True)
        self.assertTrue(self.device.oscillation_toggle)

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.toggle_oscillation(self.govee, False)
        self.assertFalse(self.device.oscillation_toggle)

    async def test_work_mode(self):
        mock_response = self.test_data["work_mode_response"]
        mock_response_custom = self.test_data["work_mode_response_custom"]
        mock_response_update = self.test_data["update_response"]

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/state",
            status=200,
            payload=mock_response_update,
        )

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.set_work_mode(self.govee, "Normal")
        self.assertEqual(self.device.work_mode, "Normal")

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response_custom,
        )
        await self.device.set_work_mode(self.govee, "Custom")
        self.assertEqual(self.device.work_mode, "Custom")

        with self.assertRaises(ValueError):
            await self.device.set_work_mode(self.govee, "Invalid")

    async def test_fan_speed(self):
        mock_response = self.test_data["fan_speed_response"]

        self.mock_aioresponse.post(
            "https://openapi.api.govee.com/router/api/v1/device/control",
            status=200,
            payload=mock_response,
        )
        await self.device.set_fan_speed(self.govee, 2)
        self.assertEqual(self.device.fan_speed, 2)

        with self.assertRaises(ValueError):
            await self.device.set_fan_speed(self.govee, 0)
        with self.assertRaises(ValueError):
            await self.device.set_fan_speed(self.govee, 9)

    async def test_update(self):
        mock_response = self.test_data["update_response"]

        with patch("devices.fan.h7102.log.warning") as mock_logging:
            self.mock_aioresponse.post(
                "https://openapi.api.govee.com/router/api/v1/device/state",
                status=200,
                payload=mock_response,
            )
            await self.device.update(self.govee)
            self.assertEqual(self.device.online, True)
            self.assertEqual(self.device.power_switch, False)
            self.assertEqual(self.device.oscillation_toggle, False)
            self.assertEqual(self.device.work_mode, "Normal")
            self.assertEqual(self.device.fan_speed, 2)
            mock_logging.assert_called_once_with(
                "Found unknown capability type devices.capabilities.unknown"
            )

    async def test_str(self):
        expected_device_str = "Name: Smart Tower Fan, SKU: H7102, Device ID: test-device-id, Online: False, Power Switch: False, Oscillation Toggle: False, Work Mode: Normal, Fan Speed: 1"
        device_str = self.device.__str__()
        assert device_str == expected_device_str
