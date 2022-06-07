#!/usr/bin/env python3
from object_detection import ObjectDetection
import argparse

class Args:
    @staticmethod
    def get_args() -> argparse.ArgumentParser:
        """ parse arguments to perform object detection with depthai """
        # parse arguments
        parser = argparse.ArgumentParser()
        parser.add_argument("-m", "--model", help="Provide model name or model path for inference",
                            default='yolov4_tiny_coco_416x416', type=str)
        parser.add_argument("-c", "--config", help="Provide config path for inference",
                            default='yolov4-tiny.json', type=str)
        parser.add_argument("-tup", "--threshold_up", help="Provide maximum depth for the sensor (mm)",
                            default=1000)
        parser.add_argument("-tdn", "--threshold_down", help="Provide minimum depth for the sensor (mm)",
                            default=50)
        return parser.parse_args()

class App(object):
    def __init__(self) -> None:
        self.args = Args.get_args()
        self.od = ObjectDetection(self.args)

    def configure(self) -> None:
        self.od.configure_pipeline()
        self.od.configure_properties()
        self.od.configure_link()

    def run(self) -> None:
        self.od.run()

if __name__ == "__main__":
    app = App()
    app.configure()
    app.run()
