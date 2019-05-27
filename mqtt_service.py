import json
import time

import paho.mqtt.client as mqtt
import redis
from walrus import Walrus

from config import REDIS_HOSTNAME, REDIS_PORT, MQTT_HOSTNAME
from mqtt_subscriber import MQTTSubscriber
from utils import retrieve_logger, get_traceback


class MQTTMicroService(object):
    MQTT_MESSAGE_INCOMING_QUEUE = "devices/mqtt"

    SLEEP_PERIOD = 5
    MAX_ATTEMPTS = 50

    def __init__(self, *args, **kwargs):
        self.logger = retrieve_logger("mqtt_forward")

        self.mqtt = mqtt.Client()
        self.mqtt.on_connect = self._on_connect_callback
        self.mqtt.on_publish = self._on_publish_callback
        self._connect_to_mqtt_broker()

        self.walrus = Walrus(REDIS_HOSTNAME, REDIS_PORT)
        self.messages_to_be_sent_to_devices_queue = self.walrus.List(self.MQTT_MESSAGE_INCOMING_QUEUE)
        self.redis_connection = redis.StrictRedis(REDIS_HOSTNAME, REDIS_PORT)

    def _connect_to_mqtt_broker(self):
        while True:
            try:
                self.mqtt.connect(MQTT_HOSTNAME)
                return
            except Exception as err:
                self.logger.error(
                    "Failed to connect to the broker. Reason: {}".format(get_traceback())
                )
                time.sleep(5)

    def _on_connect_callback(self, client, userdata, flags, rc):
        self.logger.debug("Connected to MQTT Broker")
        self.logger.debug("Connected flags" + str(flags) + "result code " + str(rc) + "client1_id ")
        client.connected_flag = True

        self.mqtt.subscribe("devices/+", qos=0)
        self.logger.info("Subscribed to 'devices/+' to receive messages from smart things")

    def _on_publish_callback(self, client, userdata, mid):
        self.logger.debug("Published data")
        self.logger.debug(client)
        self.logger.debug(userdata)
        self.logger.debug(mid)

    @staticmethod
    def _get_mqtt_forward_message_topic(device_uuid):
        return "devices/{}/forward".format(device_uuid)

    def forward_to_device(self, device_info, message):
        device_uuid = device_info["device_uuid"]
        device_mqtt_topic = self._get_mqtt_forward_message_topic(device_uuid)
        body = {
            "message": message,
        }

        attempts = 0
        while attempts < self.MAX_ATTEMPTS:
            self.logger.debug(
                "Attempt {}. Publish message {} to topic {}"
                    .format(attempts, body, device_mqtt_topic)
            )

            try:
                self.mqtt.publish(device_mqtt_topic, json.dumps(body), qos=0)
                self.logger.debug("Message was published to topic: {}".format(device_mqtt_topic))
                return

            except Exception as err:
                self.logger.error("Failed to send the message to the device {}. Reason: {}".format(device_uuid, err))
                self.logger.info("Sleep a period before retrying to send the message to device {}".format(device_uuid))

                attempts += 1
                time.sleep(self.SLEEP_PERIOD)

        raise Exception("Failed to forward the message")

    def run(self):
        # For the component that lister for message device
        mqtt_subscriber = MQTTSubscriber(MQTT_HOSTNAME, self.logger)
        mqtt_subscriber.start()

        self.logger.info("Started MQTT Forward Micro-Service")
        while True:
            message = self.messages_to_be_sent_to_devices_queue.bpopleft(timeout=120)
            if not message:
                continue

            message = json.loads(message.decode("utf-8"))
            try:
                self.logger.info("Received message from GASS: {}".format(message))
                self.forward_to_device(message["device_info"], message["value"])
            except Exception as err:
                self.logger.error(err, exc_info=True)
                continue

            self.logger.debug("Waiting for message")


if __name__ == '__main__':
    mqtt_forward = MQTTMicroService()
    mqtt_forward.run()
