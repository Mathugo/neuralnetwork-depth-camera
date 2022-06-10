#!/usr/bin/env python3
from src.runtime.object_detection import ObjectDetection
from src.mqtt.client import Mqtt_Client
from src.api import app
from src.niryo import Niryo
import argparse

class Args:
    @staticmethod
    def get_args() -> argparse.ArgumentParser:
        """ parse arguments to perform object detection with depthai """

        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--model", help="Provide model name for inference",
                            default='yolov5m_default_openvino_2021.4_6shave.blob', type=str)
        parser.add_argument("-c", "--config", help="Provide json config for inference",
                            default='yolov5', type=str),
        parser.add_argument("-mb", "--mqtt_broker", help="Provide the address of the mqtt broker", 
                            default='test.fr', type=str),
        parser.add_argument("-mt", "--mqtt_topic", help="Provide the topic for the mqtt client",
                            default='results/object_detetction', type=str),
        parser.add_argument("-tup", "--threshold_up", help="Provide maximum depth for the sensor (mm)",
                            default=1000)
        parser.add_argument("-tdn", "--threshold_down", help="Provide minimum depth for the sensor (mm)",
                            default=50)
        return parser.parse_args()

class App(object):
    def __init__(self):
        """ start depthai, api, niryo"""
        self.args = Args.get_args()
        self._od = ObjectDetection(self.args)
        self._ni = Niryo()
        self._api = None
        self._mqtt_client = None
        #self.mqtt_client = Mqtt_Client(self.args.mqtt_broker, self.args.mqtt_topic)

    def configure(self) -> None:
        self._od.configure_pipeline()
        self._od.configure_properties()
        self._od.configure_link()

    def run(self) -> None:
        self._od.run()

if __name__ == "__main__":
    APP = App()
    APP.configure()
    APP.run()