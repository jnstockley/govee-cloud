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
    response = await response.json()
    if response["code"] != 200 or response["message"] != "success":
        raise RuntimeError(
            f"Request failed with error code {response['code']} and message {response['message']}"
        )
    if "data" not in response:
        raise RuntimeError("Response does not contain data")


def validate_data(data: dict) -> bool:
    if "requestId" not in data or type(data["requestId"]) is not str:
        raise ValueError("data must contain a requestId")
    if "payload" not in data or type(data["payload"]) is not dict:
        raise ValueError("data must contain a payload")
    if type(data["payload"]) is not dict:
        raise ValueError("payload must be a dictionary")
    payload: dict = data["payload"]
    # TODO See if we can validate the payload further
    if "sku" not in payload or type(payload["sku"]) is not str:
        raise ValueError("payload must contain a sku")
    if "device" not in payload or type(payload["device"]) is not str:
        raise ValueError("payload must contain a device")
    if "capability" not in payload:
        raise ValueError("payload must contain a capability")
    if type(payload["capability"]) is not dict:
        raise ValueError("capability must be a dictionary")
    capability: dict = payload["capability"]
    if "type" not in capability or type(capability["type"]) is not str:
        raise ValueError("capability must contain a type")
    if "instance" not in capability or type(capability["instance"]) is not str:
        raise ValueError("capability must contain an instance")
    if "value" not in capability or type(capability["value"]) is not str:
        raise ValueError("capability must contain a value")
    if capability["type"] not in capabilities:
        raise ValueError(f"capability type {capability['type']} is not supported")
    if capability["instance"] not in capabilities[capability["type"]]:
        raise ValueError(
            f"capability instance {capability['instance']} is not supported for type {capability['type']}"
        )
    return True


class GoveeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openapi.api.govee.com"
        self.headers = {
            "Govee-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        self.client = aiohttp.ClientSession(
            base_url=self.base_url,
            headers=self.headers,
            raise_for_status=validate_response,
        )

    async def get_devices(self):
        async with self.client.get("/router/api/v1/user/devices") as response:
            json = await response.json()
            return json["data"]

    async def control_device(self, data: dict):
        if validate_data(data):
            async with self.client.post(
                "/router/api/v1/device/control", json=data
            ) as response:
                return await response.json()

    async def get_device_state(self):
        async with self.client.post("/router/api/v1/device/state") as response:
            return await response.json()

    async def get_dynamic_device(self):
        async with self.client.post("/router/api/v1/device/scenes") as response:
            return await response.json()
