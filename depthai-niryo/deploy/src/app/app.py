import argparse, sys, os

sys.path.append("/app/build/python_tcp_client")
sys.path.append("/app/models/")
sys.path.append("/app/config/")

from ..runtime import ObjectDetection
from ..mqtt import MqttClient
from ..niryo import Niryo

""" DEFAULT ARGS """

DEFAULT_MODEL = "yolov5m_default_openvino_2021.4_6shave.blob"
DEFAULT_CONFIG = "yolov5.json"
DEFAULT_MQTT_BROKER = "test.fr"
DEFAULT_MQTT_NIRYO_TOPIC = "mqtt/niryo/"
DEFAULT_MQTT_CAM_TOPIC = "mqtt/cam/"
DEFAULT_MQTT_BROKER_PORT = "1883"

DEFAULT_THRESH_UP = 1000
DEFAULT_THRESH_DOWN = 50

class Args:
    @staticmethod
    def get_args() -> dict:
        """ parse arguments to perform object detection with depthai 

        model :             string -> Provide model name for inference (models located in deploy/models)
        config:             string -> Provide json config for inference (configs located in deploy/configs)
        mqtt_broker:        string -> Provide the address of the mqtt broker
        mqtt_niryo_topic:   string -> Provide the niryo topic for the mqtt client
        mqtt_cam_topic:     string -> Provide the camera topic for the mqtt client
        threshold_up:       string -> Provide maximum depth for the sensor (mm)
        threshold_down:     string -> Provide minimum depth for the sensor (mm)
        """

        _args = {}
        _args["model"] = os.environ.get("MODEL", DEFAULT_MODEL)
        _args["config"] = os.environ.get("CONFIG", DEFAULT_CONFIG)
        _args["mqtt_broker"] = os.environ.get("MQTT_BROKER", DEFAULT_MQTT_BROKER)
        _args["mqtt_niryo_topic"] = os.environ.get("MQTT_NIRYO_TOPIC", DEFAULT_MQTT_NIRYO_TOPIC)
        _args["mqtt_cam_topic"] = os.environ.get("MQTT_CAM_TOPIC", DEFAULT_MQTT_CAM_TOPIC)
        _args["mqtt_broker_port"] = os.environ.get("MQTT_BROKER_PORT", DEFAULT_MQTT_BROKER_PORT)
        _args["threshold_up"] = os.environ.get("THRESHOLD_UP", DEFAULT_THRESH_UP)
        _args["threshold_down"] = os.environ.get("THRESHOLD_DOWN", DEFAULT_THRESH_DOWN)
        return _args

class App(object):
    def __init__(self):
        """ start depthai, api, niryo"""
        self._args = Args.get_args()
        #self._ni = Niryo()
        self._ni = None
        self._mqtt_client = MqttClient(self._args["mqtt_broker"], self._args["mqtt_cam_topic"], self._args["mqtt_niryo_topic"], int(self._args["mqtt_broker_port"]))
        self._od = ObjectDetection(self._args, mqtt_client=self._mqtt_client)

    def configure(self) -> None:
        self._od.configure_pipeline()
        self._od.configure_properties()
        self._od.configure_link()

    def run(self) -> None:
        self._od.run()

    def __del__(self):
        self.exit()
    
    def exit(self) -> None: 
        pass
        #self._mqtt_client.quit()
        #self._ni.quit()