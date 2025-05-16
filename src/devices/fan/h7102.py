"""Smart Tower Fan"""

import logging
from devices.device_type import DeviceType
from util.govee_api import GoveeAPI

log = logging.getLogger(__name__)


class H7102:
    def __init__(self, device_id: str):
        self.work_mode_dict = {
            1: "Normal",
            2: "Custom",
            3: "Auto",
            5: "Sleep",
            6: "Nature",
        }
        self.sku: str = "H7102"
        self.device_id: str = device_id
        self.device_name: str = "Smart Tower Fan"
        self.device_type: DeviceType = DeviceType.FAN
        self.online: bool = False
        self.power_switch: bool = False
        self.oscillation_toggle: bool = False
        self.work_mode: str = self.work_mode_dict[1]
        self.fan_speed: int = 1
        self.min_fan_speed: int = 1
        self.max_fan_speed: int = 8

    def __str__(self):
        return f"Name: {self.device_name}, SKU: {self.sku}, Device ID: {self.device_id}, Online: {self.online}, Power Switch: {self.power_switch}, Oscillation Toggle: {self.oscillation_toggle}, Work Mode: {self.work_mode}, Fan Speed: {self.fan_speed}"

    async def update(self, api: GoveeAPI):
        """
        Update the device state
        :param api: The Govee API
        """
        try:
            state = await api.get_device_state(self.sku, self.device_id)
            capabilities: dict = state["capabilities"]
            for capability in capabilities:
                capability_type: str = capability["type"]
                if capability_type == "devices.capabilities.online":
                    self.online = capability["state"]["value"]
                elif capability_type == "devices.capabilities.on_off":
                    self.power_switch = capability["state"]["value"] == 1
                elif capability_type == "devices.capabilities.toggle":
                    self.oscillation_toggle = capability["state"]["value"] == 1
                elif capability_type == "devices.capabilities.work_mode":
                    self.work_mode = self.work_mode_dict[
                        capability["state"]["value"]["workMode"]
                    ]
                    self.fan_speed = capability["state"]["value"]["modeValue"]
                else:
                    log.warning(f"Found unknown capability type {capability_type}")
        except Exception as e:
            self.online = False
            log.error(f"Error updating device state: {e}")

    def parse_response(self, response: dict):
        capability_type = response["type"]
        if capability_type == "devices.capabilities.on_off":
            self.power_switch = response["value"] == 1
        elif capability_type == "devices.capabilities.toggle":
            self.oscillation_toggle = response["value"] == 1
        elif capability_type == "devices.capabilities.work_mode":
            self.work_mode = self.work_mode_dict[response["value"]["workMode"]]
            self.fan_speed = response["value"]["modeValue"]
        else:
            log.warning(f"Found unknown capability type {capability_type}")

    async def turn_on(self, api: GoveeAPI):
        """
        Turn on the device
        :param api: The Govee API
        """
        capability = {
            "type": "devices.capabilities.on_off",
            "instance": "powerSwitch",
            "value": 1,
        }
        response = await api.control_device(self.sku, self.device_id, capability)
        self.parse_response(response)

    async def turn_off(self, api: GoveeAPI):
        """
        Turn off the device
        :param api: The Govee API
        """
        capability = {
            "type": "devices.capabilities.on_off",
            "instance": "powerSwitch",
            "value": 0,
        }
        response = await api.control_device(self.sku, self.device_id, capability)
        self.parse_response(response)

    async def toggle_oscillation(self, api: GoveeAPI, oscillation: bool):
        """
        Control the oscillation of the device
        :param api: The Govee API
        :param oscillation: True to turn on oscillation, False to turn off oscillation
        """
        capability = {
            "type": "devices.capabilities.toggle",
            "instance": "oscillationToggle",
            "value": 1 if oscillation else 0,
        }
        response = await api.control_device(self.sku, self.device_id, capability)
        self.parse_response(response)

    async def set_work_mode(self, api: GoveeAPI, work_mode: str):
        """
        Set the work mode of the device
        :param api: The Govee API
        :param work_mode: The work mode to set, must be in self.work_mode_dict.values()
        """
        if work_mode not in self.work_mode_dict.values():
            raise ValueError(f"Invalid work mode {work_mode}")

        if work_mode == "Normal":
            await self.update(api)
            value = {"workMode": 1, "modeValue": self.fan_speed}
        else:
            work_mode_key = None
            for key, value in self.work_mode_dict.items():
                if value == work_mode:
                    work_mode_key = key
            value = {"workMode": work_mode_key, "modeValue": 0}

        capability = {
            "type": "devices.capabilities.work_mode",
            "instance": "workMode",
            "value": value,
        }

        response = await api.control_device(self.sku, self.device_id, capability)
        self.parse_response(response)

    async def set_fan_speed(self, api: GoveeAPI, fan_speed: int):
        """
        Set the fan speed of the device
        :param api: The Govee API
        :param fan_speed: The fan speed to set, must be between self.min_fan_speed and self.max_fan_speed
        """
        if fan_speed < self.min_fan_speed or fan_speed > self.max_fan_speed:
            raise ValueError(
                f"Fan speed must be between {self.min_fan_speed} and {self.max_fan_speed}"
            )

        capability = {
            "type": "devices.capabilities.work_mode",
            "instance": "workMode",
            "value": {"workMode": 1, "modeValue": fan_speed},
        }
        response = await api.control_device(self.sku, self.device_id, capability)
        self.parse_response(response)
