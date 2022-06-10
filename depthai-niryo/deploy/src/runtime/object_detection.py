import argparse
import json
from pathlib import Path
import string
import time
import cv2
import os
import depthai as dai

class ObjectDetection(object):
    def __init__(self, args: argparse.ArgumentParser, model_basename: string="models", config_basename: string="config") -> None:
        """ get initial config based on given files """
        # parse config
        self.args = args
        self.configPath = Path(os.path.join(config_basename, args.config))
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
        self.nnPath = Path(os.path.join(model_basename, args.model))
        if not Path(self.nnPath).exists():
            raise ValueError("Path {} does not exist!".format(self.nnPath))
        # sync outputs
        self.syncNN = True
        
    def configure_pipeline(self) -> None:
        """ configure the video pipeline """
        # Create pipeline
        print("[!] Setting up video pipeline ..")
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
        print("[*] Done ! ")
    
    def configure_properties(self) -> None:
        """ configure camera and neural network properties for object detection """
        # Properties
        self.camRgb.setPreviewSize(self.W, self.H)

        """ rgb """
        self.camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
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
        self.spatialDetectionNetwork.setDepthLowerThreshold(self.args.threshold_down)
        self.spatialDetectionNetwork.setDepthUpperThreshold(self.args.threshold_up)

        # TODO what is this parameter doing ?
        self.spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
    
    def configure_link(self) -> None:
        """ configure link for all sources """

        print("[!] Linking all sources ..")
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
        print("[*] Done")

    @staticmethod
    def draw(rgb_frame, depth_frame, detections, labels, fps: int=0, show: bool=True, color: tuple=(255, 255, 255)):
        """ draw detection on frame """
        height = rgb_frame.shape[0]
        width  = rgb_frame.shape[1]
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

            cv2.rectangle(rgb_frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.putText(rgb_frame, "NN fps: {:.2f}".format(fps), (2, rgb_frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
        
        if show:
            cv2.imshow("depth", depth_frame)
            cv2.imshow("rgb", rgb_frame)
    
    async def run(self) -> None:
        print("[!] Run started")
        # Connect to device and start pipeline
        with dai.Device(self.pipeline) as device:

            # Output queues will be used to get the rgb frames and nn data from the outputs defined above
            previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
            detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
            xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
            depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

            startTime = time.monotonic()
            counter = 0
            fps = 0
            color = (255, 255, 255)

            while True:
                inPreview = previewQueue.get()
                inDet = detectionNNQueue.get()
                depth = depthQueue.get()

                frame = inPreview.getCvFrame()
                depthFrame = depth.getFrame() # depthFrame values are in millimeters

                depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
                depthFrameColor = cv2.equalizeHist(depthFrameColor)
                depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

                counter+=1
                current_time = time.monotonic()
                if (current_time - startTime) > 1 :
                    fps = counter / (current_time - startTime)
                    counter = 0
                    startTime = current_time

                detections = inDet.detections
                if len(detections) != 0:
                    boundingBoxMapping = xoutBoundingBoxDepthMappingQueue.get()
                    roiDatas = boundingBoxMapping.getConfigData()

                    for roiData in roiDatas:
                        roi = roiData.roi
                        roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
                        topLeft = roi.topLeft()
                        bottomRight = roi.bottomRight()
                        xmin = int(topLeft.x)
                        ymin = int(topLeft.y)
                        xmax = int(bottomRight.x)
                        ymax = int(bottomRight.y)

                        cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

                # If the frame is available, draw bounding boxes on it and show the frame
                ObjectDetection.draw(frame, depthFrameColor, detections, self.labels, fps=fps, color=color)

                if cv2.waitKey(1) == ord('q'):
                    print("[*] Exiting ..")
                    break

