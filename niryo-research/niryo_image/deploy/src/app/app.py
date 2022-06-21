from src.niryo import Niryo
import argparse

""" Global variables """
mustStop = False

""" DEFAULT ARGS """

DEFAULT_MQTT_BROKER = "test.fr"
DEFAULT_MQTT_NIRYO_TOPIC = "niryo/"
DEFAULT_MQTT_CAM_TOPIC = "cam/"
DEFAULT_NIRYO_IP = "localhost"

class Args:
    @staticmethod
    def get_args() -> dict:
        """ parse arguments to perform object detection with depthai 
        
        mqtt_broker:        string -> Provide the address of the mqtt broker
        mqtt_niryo_topic:   string -> Provide the niryo topic for the mqtt client
        niryo_ip:           string -> Provide niryo ip address
        """

        _args = {}
        _args["mqtt_broker"] = os.environ.get("MQTT_BROKER", DEFAULT_MQTT_BROKER)
        _args["mqtt_niryo_topic"] = os.environ.get("MQTT_NIRYO_TOPIC", DEFAULT_MQTT_NIRYO_TOPIC)
        _args["mqtt_cam_topic"] = os.environ.get("MQTT_CAM_TOPIC", DEFAULT_MQTT_CAM_TOPIC)
        _args["niryo_ip"] = os.environ.get("NIRYO_IP", DEFAULT_NIRYO_IP)

        return _args

class App:
    def __init__(self):
        self._args = get_args()
        self._n = Niryo(self._args["niryo_ip"])
    
    def run(self):
        global mustStop
        while not mustStop:
            # read mqtt topic
            # launch niryo position according to that
            pass
