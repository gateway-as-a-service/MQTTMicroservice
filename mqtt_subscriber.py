import json
import threading

import paho.mqtt.client as mqtt
from walrus import Walrus

from config import REDIS_HOSTNAME, REDIS_PORT


class MQTTSubscriber(threading.Thread):
    DEVICES_MESSAGES_QUEUE = "devices_messages"

    def __init__(self, broker_address, logger):
        super().__init__()

        self.logger = logger
        self.walrus = Walrus(REDIS_HOSTNAME, REDIS_PORT)
        self.messages_from_devices_queue = self.walrus.List(self.DEVICES_MESSAGES_QUEUE)

        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self._on_connect_callback
        self.mqtt.on_message = self._process_message_received
        self.mqtt.connect(broker_address)

    def _on_connect_callback(self, client, userdata, flags, rc):
        self.logger.info("Connected to MQTT Broker")
        client.connected_flag = True
        self.mqtt.subscribe("devices/+", qos=0)

    def _process_message_received(self, client, user_data, message):
        try:
            self.logger.info("Topic: {}".format(message.topic))
            parsed_message = json.loads(message.payload.decode("utf-8"))
            self.logger.info("Message: {}".format(parsed_message))

            self._send_to_processing(parsed_message)

            self.logger.info("Message has been sent to be processed")

        except Exception as err:
            self.logger.error(err)

    def _send_to_processing(self, message):
        self.messages_from_devices_queue.append(json.dumps(message))
        # TODO: Try for a fixed number of times to send the message

    def run(self):
        self.mqtt.loop_forever()
