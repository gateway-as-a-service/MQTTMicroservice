import os

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

print(os.environ.get('APP_ENV'))
if os.environ.get('APP_ENV') == 'docker':
    MQTT_HOSTNAME = "docker.for.win.localhost"
    REDIS_HOSTNAME = "docker.for.win.localhost"
else:
    MQTT_HOSTNAME = "127.0.0.1"
    REDIS_HOSTNAME = "127.0.0.1"

REDIS_PORT = 6379
MQTT_PORT = 1883

DEVICES_MESSAGES_QUEUE = "devices_messages"
