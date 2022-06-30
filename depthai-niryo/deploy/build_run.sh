#!/bin/bash

run () {
  sudo docker run -it \
    --net=host \
    --name=ofb-depthai \
    --env MQTT_BROKER="192.168.1.39" \
    --env MQTT_BROKER_PORT="4003" \
    --env MQTT_CAM_TOPIC="cam" \
    --env MQTT_NIRYO_TOPIC="niryo" \
    --env MODEL=yolov5_openvino_2021.4_6shave.blob \
    --env CONFIG=gear_yolov5.json --rm \
    --privileged \
    -v /dev/bus/usb:/dev/bus/usb \
    --device-cgroup-rule='c 189:* rmw' \
    mathugo/ofb-depthai 
}

buid () {
  sudo docker build -t mathugo/ofb-depthai .
}

if [ $# -eq 0 ]; then
  echo "No arguments supplied, building image .."
  build
  run
  
elif [ $1 == "--run" ]; then
  echo "Running the image .."
  run
fi

