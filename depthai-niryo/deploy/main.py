#!/usr/bin/python3
import argparse, sys, os
sys.path.append("/app/build/python_tcp_client")
from signal import signal, SIGINT
from src.runtime.object_detection import ObjectDetection
from src.mqtt.client import Mqtt_Client
from src.api import app
from src.niryo import Niryo

""" DEFAULT ARGS """

DEFAULT_MODEL = "yolov5m_default_openvino_2021.4_6shave.blob"
DEFAULT_CONFIG = "yolov5.json"
DEFAULT_MQTT_BROKER = "test.fr"
DEFAULT_MQTT_TOPIC = "results/object_detection"
DEFAULT_THRESH_UP = 1000
DEFAULT_THRESH_DOWN = 50

class Args:
    @staticmethod
    def get_args() -> dict:
        """ parse arguments to perform object detection with depthai 

        model :         string -> Provide model name for inference (models located in deploy/models)
        config:         string -> Provide json config for inference (configs located in deploy/configs)
        mqtt_broker:    string -> Provide the address of the mqtt broker
        mqtt_topic:     string -> Provide the topic for the mqtt client
        threshold_up:   string -> Provide maximum depth for the sensor (mm)
        threshold_down: string -> Provide minimum depth for the sensor (mm)
        """

        _args = {}
        _args["model"] = os.environ.get("MODEL", DEFAULT_MODEL)
        _args["config"] = os.environ.get("CONFIG", DEFAULT_CONFIG)
        _args["mqtt_broker"] = os.environ.get("MQTT_BROKER", DEFAULT_MQTT_BROKER)
        _args["mqtt_topic"] = os.environ.get("MQTT_TOPIC", DEFAULT_MQTT_TOPIC)
        _args["threshold_up"] = os.environ.get("THRESHOLD_UP", DEFAULT_THRESH_UP)
        _args["threshold_down"] = os.environ.get("THRESHOLD_DOWN", DEFAULT_THRESH_DOWN)
        return _args

class App(object):
    def __init__(self):
        """ start depthai, api, niryo"""
        self.args = Args.get_args()
        self._ni = Niryo()
        self._od = ObjectDetection(self.args, self._ni)
        self._api = None
        self._mqtt_client = None
        #self.mqtt_client = Mqtt_Client(self.args.mqtt_broker, self.args.mqtt_topic)

    def configure(self) -> None:
        self._od.configure_pipeline()
        self._od.configure_properties()
        self._od.configure_link()

    def run(self) -> None:
        self._od.run()

    def handler(self, signal_received, frame):
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        self._ni.quit()
        self
        exit(0)

if __name__ == "__main__":
    APP = App()
    APP.configure()
    APP.handler(SIGINT, handler)
    print('Running. Press CTRL-C to exit.')
    APP.run()