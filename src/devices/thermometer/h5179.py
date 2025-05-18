"""Wi-Fi Thermometer"""

import logging

from devices.device_type import DeviceType
from util.govee_api import GoveeAPI

log = logging.getLogger("govee-cloud")


class H5179:
    def __init__(self, device_id: str):
        self.sku: str = "H5179"
        self.device_id: str = device_id
        self.device_name: str = "Wi-Fi Thermometer"
        self.device_type: DeviceType = DeviceType.THERMOMETER
        self.online: bool = False
        self.temperature: float = 0.0
        self.humidity: float = 0.0

    def __str__(self):
        return f"Name: {self.device_name}, Device ID: {self.device_id}, Online: {self.online}, Temperature: {self.temperature}F, Humidity: {self.humidity}%"

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
                    print(capability["state"]["value"])
                    self.online = capability["state"]["value"]
                elif capability_type == "devices.capabilities.property":
                    instance = capability["instance"]
                    if instance == "sensorTemperature":
                        self.temperature = capability["state"]["value"]
                    elif instance == "sensorHumidity":
                        self.humidity = capability["state"]["value"]
                    else:
                        log.warning(f"Found unknown instance {instance}")
                        continue
                else:
                    log.warning(f"Found unknown capability type {capability_type}")
        except Exception as e:
            self.online = False
            log.error(f"Error updating device state: {e}")
