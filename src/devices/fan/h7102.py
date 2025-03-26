"""Smart Tower Fan"""

import logging
from devices.device_type import DeviceType
from util.govee_api import GoveeAPI
from util.govee_appliance_api import GoveeApplianceAPI

log = logging.getLogger(__name__)


class H7102:
    def __init__(self, device_id: str):
        self.work_mode_dict = {
            1: "Normal",
            2: "Custom",
            3: "Normal",
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
        await api.control_device(self.sku, self.device_id, capability)
        self.power_switch = True

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
        await api.control_device(self.sku, self.device_id, capability)
        self.power_switch = False

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
        await api.control_device(self.sku, self.device_id, capability)
        self.oscillation_toggle = oscillation

    # TODO API Returns failure when setting work mode to anything but Normal (1)
    async def set_work_mode(self, api: GoveeApplianceAPI, work_mode: str):
        """
        Set the work mode of the device
        :param api: The Govee API
        :param work_mode: The work mode to set, must be in self.work_mode_dict.values()
        """
        if work_mode not in self.work_mode_dict.values():
            raise ValueError(f"Invalid work mode {work_mode}")

        work_mode_key = None
        for key, value in self.work_mode_dict.items():
            if value == work_mode:
                work_mode_key = key

        cmd = {"name": "mode", "value": work_mode_key}

        await api.control_device(self.sku, self.device_id, cmd)
        self.work_mode = work_mode

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

        work_mode_key = None
        for key, value in self.work_mode_dict.items():
            if value == self.work_mode:
                work_mode_key = key

        capability = {
            "type": "devices.capabilities.work_mode",
            "instance": "workMode",
            "value": {"workMode": work_mode_key, "modeValue": fan_speed},
        }
        await api.control_device(self.sku, self.device_id, capability)
        self.fan_speed = fan_speed
