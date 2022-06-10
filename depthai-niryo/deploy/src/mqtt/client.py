import string
import paho.mqtt.client as mqtt #import the client1

class Mqtt_Client(object):
    def __init__(self, broker_addr: string, topic: string, broker_port: int=1883, client_name: string="niryo") -> None:
        """ initialize an mqtt client for the niryo"""

        print("[*] Creating {} client ..".format(client_name))
        self._client = mqtt.Client(client_name)
        self._topic = topic
        print("[*] Connecting to broker {} ..".format(broker_addr))
        self._client.connect(broker_addr, broker_port, keepalive=60, bind_address="") 
        print("[*] Done")
        print("[*] Subscribing to topic {} ..".format(topic))
        self._client.subscribe(topic)
        print("[*] Done")
    
    def publish(self, msg: string) -> None:
        """ publish a message on the subscribed topic"""
        
        print("[!] Publishing message {} ..".format(msg))
        self._client.publish(self._topic, msg)
