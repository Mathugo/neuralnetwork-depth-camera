from ..runtime import ObjectDetection
from ..mqtt import MqttClient
from ..niryo import Niryo
from ..utils import global_var
from .args import Args

class App(object):
    """App class managing Niryo, ObjectDetection and MQTT client
    
    Attributes:
        _args        (dict)             : Dictionnary of all arguments passed via ``docker run``command
        _mqtt_client (MqttClient)       : MQTT Client publishing and subscribing to different topics
        _od          (ObjectDetection)  : ObjectDetection class to use depthai camera and perform object detection on video stream
    """
    def __init__(self) -> None:
        """Start Niryo robot, MQTT client and object detection models"""

        self._args = Args.get_args()
        self._mqtt_client = MqttClient(self._args["mqtt_broker"], self._args["mqtt_cam_topic"], self._args["mqtt_niryo_topic"], int(self._args["mqtt_broker_port"]), verbose=self._args["mqtt_verbose"])
        global_var.NIRYO = Niryo()
        self._od = ObjectDetection(self._args, mqtt_client=self._mqtt_client)

    def configure(self) -> None:
        """Configure object detection properties and its pipeline"""

        self._od.configure_pipeline()
        self._od.configure_properties()
        self._od.configure_link()

    def run(self) -> None:
        """Run the main loop of object detection

        Note:
            This will run until a environment variable MUST_STOP is set to True by the API

        """
        self._od.run()

    def __del__(self):
        self.exit()
    
    def exit(self) -> None: 
        """Safely exit the app"""
        
        print("[APP] Quitting ..")
        if global_var.NIRYO != None : global_var.NIRYO.quit()        
        if self._mqtt_client != None: self._mqtt_client.quit()
        