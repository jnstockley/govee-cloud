"""Smart Air Purifier"""

import logging
import time

from devices.device_type import DeviceType
from util.govee_api import GoveeAPI

log = logging.getLogger(__name__)


class H7126:
    def __init__(self, device_id: str):
        self.work_mode_dict = {
            1: "Sleep",
            2: "Low",
            3: "High",
            4: "Custom",
        }
        self.sku: str = "H7126"
        self.device_id: str = device_id
        self.device_name: str = "Smart Air Purifier"
        self.device_type: DeviceType = DeviceType.AIR_PURIFIER
        self.online: bool = False
        self.power_switch: bool = False
        self.work_mode: str = self.work_mode_dict[1]
        self.filter_life: int = 0
        self.air_quality: int = 0

    def __str__(self):
        return f"Name: {self.device_name}, SKU: {self.sku}, Device ID: {self.device_id}, Online: {self.online}, Power Switch: {self.power_switch}, Work Mode: {self.work_mode}, Filter Life: {self.filter_life}, Air Quality: {self.air_quality}"

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
            elif capability_type == "devices.capabilities.work_mode":
                if capability["state"]["value"]["workMode"] == 2:
                    self.work_mode = "Custom"
                else:
                    self.work_mode = self.work_mode_dict[
                        capability["state"]["value"]["modeValue"]
                    ]
            elif capability_type == "devices.capabilities.property":
                instance = capability["instance"]
                if instance == "filterLifeTime":
                    self.filter_life = capability["state"]["value"]
                elif instance == "airQuality":
                    self.air_quality = capability["state"]["value"]
                else:
                    log.warning(f"Found unknown instance {instance}")
                    continue
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

    async def set_work_mode(self, api: GoveeAPI, work_mode: str):
        """
        Set the work mode of the device
        :param api: The Govee API
        :param work_mode: The work mode to set, must be in self.work_mode_dict.values()
        """
        if work_mode not in self.work_mode_dict.values():
            raise ValueError(f"Invalid work mode {work_mode}")

        if work_mode == "Custom":
            value = {"workMode": 2, "modeValue": 0}
        else:
            work_mode_key = None
            for key, value in self.work_mode_dict.items():
                if value == work_mode:
                    work_mode_key = key

            value = {"workMode": 1, "modeValue": work_mode_key}

        capability = {
            "type": "devices.capabilities.work_mode",
            "instance": "workMode",
            "value": value,
        }

        await api.control_device(self.sku, self.device_id, capability)
        self.work_mode = work_mode
        # Add a delay to allow the device to update
        time.sleep(0.5)
