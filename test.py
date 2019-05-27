import json

import redis


def publish():
    redis_client = redis.StrictRedis("127.0.0.1", 6379)
    redis_client.pubsub()

    channel = "devices/mqtt"
    message = {
        "device_info": {
            "device_uuid": "0a9c8868-5ba4-4b18-bf92-320971118425",
            "protocol": "MQTT",
            "ip": "127.0.0.1",
            "port": 0
        },
        "value": 14
    }
    redis_client.publish(channel, json.dumps(message))
