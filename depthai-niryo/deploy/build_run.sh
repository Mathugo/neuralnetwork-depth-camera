docker build -t mathugo/ofb-depthai .
docker run -it \
  --net=host \
  --name=ofb-depthai \
  --env MQTT_BROKER="192.168.1.150" \
  --env MQTT_BROKER_PORT="4002" \
  --env MQTT_CAM_TOPIC="mqtt/cam" \
  --env MQTT_NIRYO_TOPIC="mqtt/niryo" \
  --env MODEL=yolov5_openvino_2021.4_6shave.blob \
  --env CONFIG=gear_yolov5.json --rm \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 189:* rmw' \
  mathugo/ofb-depthai 