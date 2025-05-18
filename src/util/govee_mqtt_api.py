import ssl
import threading
import logging

import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion

logger = logging.getLogger("govee-cloud")


class MqttGoveeAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.emqx_url = "mqtt.openapi.govee.com"
        self.port = 8883
        self.client_thread = None
        self.is_running = False

        # Callback when connection is established
        def on_connect(client: mqtt.Client, userdata, flags, rc, properties=None):
            logger.info("Connected to the broker with result code " + str(rc))
            client.subscribe(api_key)
            logger.info("Subscribed to topic apiKey")

        # Create MQTT client instance with explicit protocol version
        self.client = mqtt.Client(CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv5)

        # Set credentials
        self.client.username_pw_set(api_key, password=api_key)

        # Configure TLS
        self.client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS)

        # Assign callbacks
        self.client.on_connect = on_connect

        # Connect to the broker
        self.client.connect(self.emqx_url, self.port, 60)

        self.start_loop()

    def start_loop(self):
        """Start the MQTT client loop in a separate thread"""
        if not self.is_running:
            print("Starting MQTT client loop")
            logger.info("Starting MQTT client loop")
            self.is_running = True
            self.client_thread = threading.Thread(target=self.client.loop_forever)
            self.client_thread.daemon = True  # Thread will exit when main program exits
            self.client_thread.start()

    def stop_loop(self):
        """Stop the MQTT client loop"""
        if self.is_running:
            self.client.loop_stop()
            self.client.disconnect()
            self.is_running = False
            if self.client_thread:
                self.client_thread.join(timeout=1.0)
