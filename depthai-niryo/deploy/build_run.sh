docker build -t ofb-depthai .
docker run -P --env MODEL=yolov5_gear_openvino_2021.4_4shave_pruned.blob \
  --env MQTT_BROKER="test.fr" \
  --env MQTT_TOPIC="results/object_detection" \
  --env CONFIG=gear_yolov5.json --rm \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 189:* rmw' \
  ofb-depthai 