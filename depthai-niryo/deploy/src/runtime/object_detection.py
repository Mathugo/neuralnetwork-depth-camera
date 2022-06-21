import os,sys, time, threading, json
import cv2
from pathlib import Path
import string
import time
import depthai as dai
from ..niryo import Niryo
from ..mqtt import MqttClient
from ..utils import global_var

class ObjectDetection(object):
    def __init__(self, args: dict, model_basename: string="models", config_basename: string="config", mqtt_client: MqttClient=None) -> None:
        """ get initial config based on given files """
        # parse config
        self.args = args
        self._mqtt_client = mqtt_client
        self.configPath = Path(os.path.join(config_basename, args["config"]))
        self.mustStop = os.environ.get("MustStop", "Error")
        if not self.configPath.exists():
            raise ValueError("Path {} does not exist!".format(self.configPath))

        with self.configPath.open() as f:
            config = json.load(f)
        self.nnConfig = config.get("nn_config", {})

        # parse input shape
        if "input_size" in self.nnConfig:
            self.W, self.H = tuple(map(int, self.nnConfig.get("input_size").split('x')))

        # extract metadata
        self.metadata = self.nnConfig.get("NN_specific_metadata", {})
        self.classes = self.metadata.get("classes", {})
        self.coordinates = self.metadata.get("coordinates", {})
        self.anchors = self.metadata.get("anchors", {})
        self.anchorMasks = self.metadata.get("anchor_masks", {})
        self.iouThreshold = self.metadata.get("iou_threshold", {})
        self.confidenceThreshold = self.metadata.get("confidence_threshold", {})

        print(self.metadata)
        # parse labels
        self.nnMappings = config.get("mappings", {})
        self.labels = self.nnMappings.get("labels", {})

        # get model path
        self.nnPath = Path(os.path.join(model_basename, args["model"]))
        if not Path(self.nnPath).exists():
            raise ValueError("Path {} does not exist!".format(self.nnPath))
        # sync outputs
        self.syncNN = True
        print("[*] Model {} loaded with config {}".format(os.path.basename(self.nnPath), os.path.basename(self.configPath)))
        
    def configure_pipeline(self) -> None:
        """ configure the video pipeline """
        # Create pipeline
        print("\n[CAM] Setting up video pipeline ..")
        self.pipeline = dai.Pipeline()

        # Define sources and outputs for RGB and DEPTH
        self.camRgb = self.pipeline.create(dai.node.ColorCamera)
        self.spatialDetectionNetwork = self.pipeline.create(dai.node.YoloSpatialDetectionNetwork)
        self.monoLeft = self.pipeline.create(dai.node.MonoCamera)
        self.monoRight = self.pipeline.create(dai.node.MonoCamera)
        self.stereo = self.pipeline.create(dai.node.StereoDepth)

        self.xoutRgb = self.pipeline.create(dai.node.XLinkOut)
        self.xoutNN = self.pipeline.create(dai.node.XLinkOut)
        self.xoutBoundingBoxDepthMapping = self.pipeline.create(dai.node.XLinkOut)
        self.xoutDepth = self.pipeline.create(dai.node.XLinkOut)

        self.xoutRgb.setStreamName("rgb")
        self.xoutNN.setStreamName("detections")
        self.xoutBoundingBoxDepthMapping.setStreamName("boundingBoxDepthMapping")
        self.xoutDepth.setStreamName("depth")

        # Increase fps : splitting device-sent XLink packets, in bytes
        self.pipeline.setXLinkChunkSize(0)
        print("[CAM] Done ! ")
    
    def configure_properties(self) -> None:
        """ configure camera and neural network properties for object detection """
        # Properties
        self.camRgb.setPreviewSize(self.W, self.H)

        """ rgb """
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self.camRgb.setInterleaved(False)
        self.camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)
        self.camRgb.setFps(40)

        """ depth """
        self.monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        self.monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self.monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        """ depth config """
        # setting node configs
        self.stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)
        # Align depth map to the perspective of RGB camera, on which inference is done
        self.stereo.setDepthAlign(dai.CameraBoardSocket.RGB)
        self.stereo.setOutputSize(self.monoLeft.getResolutionWidth(), self.monoLeft.getResolutionHeight())

        # Network specific settings
        self.spatialDetectionNetwork.setConfidenceThreshold(self.confidenceThreshold)
        self.spatialDetectionNetwork.setNumClasses(self.classes)
        self.spatialDetectionNetwork.setCoordinateSize(self.coordinates)
        self.spatialDetectionNetwork.setAnchors(self.anchors)
        self.spatialDetectionNetwork.setAnchorMasks(self.anchorMasks)
        self.spatialDetectionNetwork.setIouThreshold(self.iouThreshold)
        self.spatialDetectionNetwork.setBlobPath(self.nnPath)
        self.spatialDetectionNetwork.setNumInferenceThreads(2)
        self.spatialDetectionNetwork.input.setBlocking(False)
        self.spatialDetectionNetwork.setDepthLowerThreshold(int(self.args["threshold_down"]))
        self.spatialDetectionNetwork.setDepthUpperThreshold(int(self.args["threshold_up"]))

        # TODO what is this parameter doing ?
        self.spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
    
    def configure_link(self) -> None:
        """ configure link for all sources """

        print("[CAM] Linking all sources ..")
        # Linking
        self.monoLeft.out.link(self.stereo.left)
        self.monoRight.out.link(self.stereo.right)
        self.camRgb.preview.link(self.spatialDetectionNetwork.input)
        if self.syncNN:
            self.spatialDetectionNetwork.passthrough.link(self.xoutRgb.input)
        else:
            self.camRgb.preview.link(self.xoutRgb.input)

        self.spatialDetectionNetwork.out.link(self.xoutNN.input)
        self.spatialDetectionNetwork.boundingBoxMapping.link(self.xoutBoundingBoxDepthMapping.input)
        self.stereo.depth.link(self.spatialDetectionNetwork.inputDepth)
        self.spatialDetectionNetwork.passthroughDepth.link(self.xoutDepth.input)
        print("[CAM] Done")

    @staticmethod
    def draw(exec_time: float, rgb_frame, depth_frame, detections, labels, fps: int=0, show: bool=False, color: tuple=(255, 255, 255)):
        """ draw detection on frame """
        height = rgb_frame.shape[0]
        width  = rgb_frame.shape[1]
        print("[*] {} detections".format(len(detections)))
        for detection in detections:
            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)
            try:
                label = labels[detection.label]
            except:
                label = detection.label

            cv2.putText(rgb_frame, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(rgb_frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(rgb_frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(rgb_frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
            cv2.putText(rgb_frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)

            print("[*] Exec Time {}ms\nObject Position ( x {}mm ; y {}mm ; z {}mm )\nclass {}\n".format(exec_time, detection.spatialCoordinates.x, detection.spatialCoordinates.y, detection.spatialCoordinates.z, detection.label))
            cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.putText(rgb_frame, "NN fps: {:.2f}".format(fps), (2, rgb_frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
        
        if show:
            cv2.imshow("depth", depth_frame)
            cv2.imshow("rgb", rgb_frame)
    
    def __counter_start(self) -> None:
        self._startTime = time.monotonic()
        self._counter = 0
        self._fps = 0

    def __counter_end(self) -> int:
        self._counter+=1
        current_time = time.monotonic()
        if (current_time - self._startTime) > 1 :
            self._fps = self._counter / (current_time - self._startTime)
            self._counter = 0
            self._startTime = current_time

    def __get_roi(self, detection) -> (int, int, int, int, int):
        """ get position from detection """

        x1 = int(detection.xmin * self._frame_width)
        x2 = int(detection.xmax * self._frame_width)
        y1 = int(detection.ymin * self._frame_height)
        y2 = int(detection.ymax * self._frame_height)
        try:
            label = self.labels[detection.label]
        except:
            label = detection.label
        return x1, x2, y1, y2, label
    
    def __get_position(self, detection) -> (float, float, float):
        return round(detection.spatialCoordinates.x, 3), round(detection.spatialCoordinates.y, 3), round(detection.spatialCoordinates.z, 3)
    
    def __get_frame(self):
        """ get frame from opencv pipeline """
        inPreview = self._previewQueue.get()
        inDet = self._detectionNNQueue.get()
        depth = self._depthQueue.get()
        frame = inPreview.getCvFrame()
        depthFrame = depth.getFrame()
        return inDet, frame, depthFrame
    
    def __publish_results(self, pos, roi):
        self._mqtt_client.publish(self._mqtt_client.cam_topic+"/pos", pos)
        self._mqtt_client.publish(self._mqtt_client.cam_topic+"/roi", roi)

    def run(self) -> None:
        print("[!] Run started")
        # Connect to device and start pipeline
        with dai.Device(self.pipeline) as device:

            # Output queues will be used to get the rgb frames and nn data from the outputs defined above
            self._previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            self._detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
            self._xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
            self._depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

            self.__counter_start()
            _, frame, _ = self.__get_frame()
            self._frame_height = frame.shape[0]
            self._frame_width  = frame.shape[1]
            print("[CAM] Height {}, Width {} of rgb frame".format(self._frame_height, self._frame_width))
        
            #color = (255, 255, 255)
            while self.mustStop != "True" and self.mustStop != "Error":
                self.mustStop = os.environ.get("MustStop", "Error")

                milli_start = int(round(time.time() * 1000))
                # depthFrame values are in millimeters
                inDet, frame, depthFrame = self.__get_frame()

                fps = self.__counter_end()
                detections = inDet.detections
                milli_end = int(round(time.time() * 1000))
                exec_time = milli_end - milli_start

                if len(detections) != 0:
                    for detection in detections:
                        x1, x2, y1, y2, label = self.__get_roi(detection)
                        x, y, z = self.__get_position(detection)
                        pos = "{}:{}:{}:{}".format(label, x, y, z)
                        roi = "{}:{}:{}:{}:{}".format(label, x1, x2, y1, y2)
                        # Here we detection the objects in our rgb and depthframe, we stop the detection 
                        # while niryo is moving (the main thread is blocked)
                        if global_var.NIRYO != None and int(x) != 0 or int(y) != 0 or int(z) != 0: 
                            print("[POS] Raw Cam Pos x {} y {} z {}".format(x, y, z))
                            global_var.NIRYO.move_to_roi(x,y,z)
                            self.__publish_results(pos, roi)

                        if self._counter % 30 == 0:
                            print("[CAM] Exec Time {}ms\nPos ( x {}mm ; y {}mm ; z {}mm )\nclass {}\nROI ({};{};{};{})".format(exec_time, x, y, z, label, x1, x2, y1, y2))                    
                            self.__publish_results(pos, roi)
                        
                if cv2.waitKey(1) == ord('q'):
                    print("[*] Exiting ..")
                    break

