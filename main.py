from mqtt_service import MQTTMicroService

if __name__ == '__main__':
    mqtt_forward = MQTTMicroService()
    mqtt_forward.run()
