import uuid

import aiohttp

capabilities = {
    "devices.capabilities.on_off": ["powerSwitch"],
    "devices.capabilities.toggle": [
        "oscillationToggle",
        "nightlightToggle",
        "airDeflectorToggle",
        "gradientToggle",
        "thermostatToggle",
        "warmMistToggle",
    ],
    "devices.capabilities.color_setting": ["colorRgb", "colorTemperatureK"],
    "devices.capabilities.mode": ["nightlightScene", "presetScene"],
    "devices.capabilities.range": ["brightness", "humidity"],
    "devices.capabilities.work_mode": ["workMode"],
    "devices.capabilities.segment_color_setting": [
        "segmentedColorRgb",
        "segmentedBrightness",
    ],
    "devices.capabilities.dynamic_scene": ["lightScene", "diyScene", "snapshot"],
    "devices.capabilities.music_setting": ["musicMode"],
    "devices.capabilities.temperature_setting": [
        "targetTemperature",
        "sliderTemperature",
    ],
}


async def validate_response(response: aiohttp.ClientResponse):
    if response.status != 200:
        raise RuntimeError(f"Request failed with status code {response.status}")
    response: dict = await response.json()
    if response["code"] != 200:
        if "msg" in response:
            raise RuntimeError(
                f"Request failed with error code {response['code']} and message {response['msg']}"
            )
        elif "message" in response:
            raise RuntimeError(
                f"Request failed with error code {response['code']} and message {response['message']}"
            )
        else:
            raise RuntimeError(f"Request failed with error code {response['code']}")
    if (
        "data" not in response
        and "payload" not in response
        and "capability" not in response
    ):
        raise RuntimeError("Response does not contain data")


def validate_capability(capability: dict) -> bool:
    if "type" not in capability or type(capability["type"]) is not str:
        raise ValueError("capability must contain a type")
    if "instance" not in capability or type(capability["instance"]) is not str:
        raise ValueError("capability must contain an instance")
    if "value" not in capability or (
        type(capability["value"]) is not int and type(capability["value"]) is not dict
    ):
        raise ValueError("capability must contain a value")
    if capability["type"] not in capabilities:
        raise ValueError(f"capability type {capability['type']} is not supported")
    if capability["instance"] not in capabilities[capability["type"]]:
        raise ValueError(
            f"capability instance {capability['instance']} is not supported for type {capability['type']}"
        )
    return True


class GoveeAPI:
    def __init__(self, api_key: str, ignore_request_id=False):
        self.api_key = api_key
        self.base_url = "https://openapi.api.govee.com"
        self.headers = {
            "Govee-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        self.ignore_request_id = ignore_request_id
        self.client = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=self.headers,
            raise_for_status=validate_response,
        )

    async def get_devices(self) -> list[dict]:
        """
        Get all devices associated with the API key
        more info: https://developer.govee.com/reference/get-you-devices
        :return: list of devices
        """
        async with self.client.get("/router/api/v1/user/devices") as response:
            json = await response.json()
            return json["data"]

    async def control_device(
        self,
        sku: str,
        device: str,
        capability: dict,
        request_id: str = str(uuid.uuid4()),
    ) -> dict | None:
        """
        Control a device
        more info: https://developer.govee.com/reference/control-you-devices
        :param sku: The SKU of the device to control
        :param device: The device ID to control
        :param capability: The capability to control
        :param request_id: Optional request ID
        :return: The capability
        """
        payload = {
            "sku": sku,
            "device": device,
            "capability": capability,
        }
        body = {"requestId": request_id, "payload": payload}
        if validate_capability(capability):
            async with self.client.post(
                "/router/api/v1/device/control", json=body
            ) as response:
                json = await response.json()
                if json["requestId"] != request_id and not self.ignore_request_id:
                    raise RuntimeError("Request ID mismatch")
                return json["capability"]

    async def get_device_state(
        self, sku: str, device: str, request_id: str = str(uuid.uuid4())
    ) -> dict:
        """
        Get the state of a device
        more info: https://developer.govee.com/reference/get-devices-status
        :param sku: The SKU of the device to get the state of
        :param device: The device ID to get the state of
        :param request_id: Optional request ID
        :return: The device
        """
        payload = {
            "sku": sku,
            "device": device,
        }
        body = {"requestId": request_id, "payload": payload}
        async with self.client.post(
            "/router/api/v1/device/state", json=body
        ) as response:
            json = await response.json()
            if json["requestId"] != request_id and not self.ignore_request_id:
                raise RuntimeError("Request ID mismatch")
            return json["payload"]

    async def get_dynamic_light_scene(
        self, sku: str, device: str, request_id: str = str(uuid.uuid4())
    ) -> dict:
        """
        Get the dynamic light scene of a light device
        :param sku: The SKU of the device to get the dynamic light scene of
        :param device: The device ID to get the dynamic light scene of
        :param request_id: Optional request ID
        :return: The dynamic light scene
        """
        payload = {
            "sku": sku,
            "device": device,
        }
        body = {"requestId": request_id, "payload": payload}
        async with self.client.post(
            "/router/api/v1/device/scenes", json=body
        ) as response:
            json = await response.json()
            if json["requestId"] != request_id and not self.ignore_request_id:
                raise RuntimeError("Request ID mismatch")
            return json["payload"]

    async def get_diy_scene(
        self, sku: str, device: str, request_id: str = str(uuid.uuid4())
    ) -> dict:
        """
        Get the DIY scene of a light device
        :param sku: The SKU of the device to get the dynamic light scene of
        :param device: The device ID to get the dynamic light scene of
        :param request_id: Optional request ID
        :return: The DIY scene
        """
        payload = {
            "sku": sku,
            "device": device,
        }
        body = {"requestId": request_id, "payload": payload}
        async with self.client.post(
            "/router/api/v1/device/diy-scenes", json=body
        ) as response:
            json = await response.json()
            if json["requestId"] != request_id and not self.ignore_request_id:
                raise RuntimeError("Request ID mismatch")
            return json["payload"]
