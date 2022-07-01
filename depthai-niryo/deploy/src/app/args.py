from typing import Dict
from os import environ
""" DEFAULT ARGS """

DEFAULT_MQTT_VERBOSE = False
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
    def get_args() -> Dict:
        """Parse arguments to perform object detection with depthai.
        This parameters are retreived using environment variables, see *main.py* for more info.

        Attributes:
            _args (:obj:`dict`): dictionnary of parameters
        
        Returns:
            dict: the formated arguments with given parameters
        """
        _args = {}
        _args["model"] = environ.get("MODEL", DEFAULT_MODEL)
        _args["config"] = environ.get("CONFIG", DEFAULT_CONFIG)
        _args["mqtt_broker"] = environ.get("MQTT_BROKER", DEFAULT_MQTT_BROKER)
        _args["mqtt_niryo_topic"] = environ.get("MQTT_NIRYO_TOPIC", DEFAULT_MQTT_NIRYO_TOPIC)
        _args["mqtt_cam_topic"] = environ.get("MQTT_CAM_TOPIC", DEFAULT_MQTT_CAM_TOPIC)
        _args["mqtt_broker_port"] = environ.get("MQTT_BROKER_PORT", DEFAULT_MQTT_BROKER_PORT)
        _args["threshold_up"] = environ.get("THRESHOLD_UP", DEFAULT_THRESH_UP)
        _args["threshold_down"] = environ.get("THRESHOLD_DOWN", DEFAULT_THRESH_DOWN)
        _args["mqtt_verbose"] = environ.get("MQTT_VERBOSE", DEFAULT_MQTT_VERBOSE)
        return _args
