import string
import paho.mqtt.client as mqtt #import the client1

DEFAULT_CLIENT_NAME = "niryo"

class MqttClient(mqtt.Client):
    def __init__(self, broker_addr: string, cam_topic: string, niryo_topic: string, broker_port: int, client_name: string=DEFAULT_CLIENT_NAME, verbose: bool=True) -> None:
        """ initialize an mqtt client for the niryo"""
        super().__init__(client_name)
        self._cam_topic = cam_topic
        self._niryo_topic = niryo_topic
        self._verbose = verbose
        print("[MQTT] Verbose {}".format(self._verbose))
        print("[MQTT] Connecting to broker {} with port {} ..".format(broker_addr, broker_port))
        try:
            self.connect(broker_addr, broker_port, keepalive=0, bind_address="")
        except:
            print("[MQTT] Unable to connect to broker {} at port {}".format(broker_addr, broker_port))
        self.loop_start()
        print("[MQTT] Done")
        print("[MQTT] Subscribing to topics {} and {} ..".format(self._cam_topic, self._niryo_topic))
        self.subscribe(cam_topic)
        self.subscribe(niryo_topic)
        print("[MQTT] Done")

    def on_message(self, client, userdata, message: string):
        """ on_message callback for the mqtt client """
        msg = str(message.payload.decode("utf-8"))
        if self._verbose:
            print("[MQTT] MSG [ {} ] FROM TOPIC [ {} ] QOS {} FLAG {}".format(msg, message.topic, message.qos, message.retain))
        self.__filter_msg(msg, message.topic)

    def publish(self, topic: string, msg: string) -> None:
        """ publish a message on a desired subscribed topic"""
        if self._verbose:
            print("[MQTT] Message {} published to broker".format(msg))
        #self.publish(topic, msg)
    
    def __filter_msg(self, msg, topic):
        if topic == self._cam_topic:
            self._cam_last_msg = msg
        else:
            self._niryo_last_msg = msg

    @property
    def client(self):
        return self

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
    
    @property
    def niryo_last_msg(self):
        return self._niryo_last_msg
    
    @niryo_last_msg.setter
    def niryo_last_msg(self, value):
        self._niryo_last_msg = value
    
    @property
    def cam_last_msg(self):
        return self._cam_last_msg
    
    @cam_last_msg.setter
    def cam_last_msg(self, value):
        self._cam_last_msg = value
    
    def quit(self):
        self.disconnect()
        self.loop_stop()
        print("[MQTT] Disconnected")

    def __del__(self):
        self.quit()

