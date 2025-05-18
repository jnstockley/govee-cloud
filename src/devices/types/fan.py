import logging

from devices.types.basic_fan import BasicFan
from util.govee_api import GoveeAPI

logger = logging.getLogger("govee-cloud")


class Fan(BasicFan):

    def __init__(self, sku: str, device_id: str, device_name: str, work_modes: dict, min_fan_speed: int, max_fan_speed: int):
        super().__init__(sku, device_id, device_name, work_modes)
        self.oscillation_toggle: bool = False
        self.fan_speed: int = 1
        self.min_fan_speed: int = min_fan_speed
        self.max_fan_speed: int = max_fan_speed

    def update(self, capability: dict):
        for capability in capability["capabilities"]:
            capability_type: str = capability["type"]
            if capability_type == "devices.capabilities.toggle":
                self.oscillation_toggle = capability["state"]["value"] == 1
            elif capability_type == "devices.capabilities.work_mode":
                self.work_mode = self.work_modes[
                    capability["state"]["value"]["workMode"]
                ]
                self.fan_speed = capability["state"]["value"]["modeValue"]
            else:
                super().update(capability)

    def parse_response(self, response: dict):
        capability_type = response["type"]
        if capability_type == "devices.capabilities.on_off":
            self.power_switch = response["value"] == 1
        elif capability_type == "devices.capabilities.toggle":
            self.oscillation_toggle = response["value"] == 1
        elif capability_type == "devices.capabilities.work_mode":
            self.work_mode = self.work_modes[response["value"]["workMode"]]
            self.fan_speed = response["value"]["modeValue"]
        else:
            logger.warning(f"Found unknown capability type {capability_type}")


    async def set_work_mode(self, api: GoveeAPI, work_mode: str):
        """
        Set the work mode of the device
        :param api: The Govee API
        :param work_mode: The work mode to set, must be in self.work_mode_dict.values()
        """
        if work_mode not in self.work_modes.values():
            raise ValueError(f"Invalid work mode {work_mode}")

        if work_mode == "Normal":
            value = {"workMode": 1, "modeValue": self.fan_speed}
        else:
            work_mode_key = None
            for key, value in self.work_modes.items():
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


