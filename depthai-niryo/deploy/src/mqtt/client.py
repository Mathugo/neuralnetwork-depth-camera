import string
import paho.mqtt.client as mqtt #import the client1

DEFAULT_BROKER_PORT = 1883
DEFAULT_CLIENT_NAME = "niryo"

class Mqtt_Client(object):
    def __init__(self, broker_addr: string, cam_topic: string, niryo_topic: string, client_name: string=DEFAULT_CLIENT_NAME, broker_port: int=DEFAULT_BROKER_PORT) -> None:
        """ initialize an mqtt client for the niryo"""

        print("[*] Creating {} client ..".format(client_name))
        self._client = mqtt.Client(client_name)
        self._cam_topic = cam_topic
        self._niryo_topic = niryo_topic
        print("[*] Connecting to broker {} ..".format(broker_addr))
        self._client.connect(broker_addr, broker_port, keepalive=60, bind_address="") 
        print("[*] Done")
        print("[*] Subscribing to topics {} and {} ..".format(self._cam_topic, self._niryo_topic))
        self._client.subscribe(cam_topic)
        self._client.subscribe(niryo_topic)
        print("[*] Done")
    
    @property
    def client(self):
        return self._client

    @property
    def cam_topic(self):
        return self._cam_topic
    
    @cam_topic.setter
    def cam_topic(self, value):
        self._cam_topic = value
    
    @property
    def niryo_topic(self):
        return self._niryo_topic
    
    @niryo_topic.setter
    def niryo_topic(self, value):
        self._niryo_topic = value

    async def publish(self, topic: string, msg: string) -> None:
        """ publish a message on a desired subscribed topic"""
        
        print("[!] Publishing message {} ..".format(msg))
        await self._client.publish(topic, msg)

    def on_message(self, client, userdata, message: string):
        print("message received " ,str(message.payload.decode("utf-8")))
        print("message topic=",message.topic)
        print("message qos=",message.qos)
        print("message retain flag=",message.retain)
    

