"""Smart Air Purifier"""

import logging
from devices.device_type import DeviceType
from util.govee_api import GoveeAPI

log = logging.getLogger(__name__)


class H7126:
    def __init__(self, device_id: str):
        self.work_mode_dict = {
            0: "Custom",
            1: "Sleep",
            2: "Low",
            3: "High",
            4: "Auto",
            5: "Custom",
        }
        self.sku: str = "H7126"
        self.device_id: str = device_id
        self.device_name: str = "Smart Air Purifier"
        self.device_type: DeviceType = DeviceType.AIR_PURIFIER
        self.online: bool = False
        self.power_switch: bool = False
        self.work_mode: str = self.work_mode_dict[1]
        self.speed: int = 1
        self.min_speed: int = 1
        self.max_speed: int = 3
        self.filter_life: int = 0
        self.air_quality: int = 0

    def __str__(self):
        return f"Name: {self.device_name}, SKU: {self.sku}, Device ID: {self.device_id}, Online: {self.online}, Power Switch: {self.power_switch}, Work Mode: {self.work_mode}, Speed: {self.speed}, Filter Life: {self.filter_life}, Air Quality: {self.air_quality}"

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
                self.work_mode = self.work_mode_dict[
                    capability["state"]["value"]["modeValue"]
                ]
                self.speed = capability["state"]["value"]["workMode"]
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
