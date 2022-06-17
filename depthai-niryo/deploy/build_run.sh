docker build -t mathugo/ofb-depthai .
docker run -it -p 4000:4000 \
  --env MQTT_BROKER="test.fr" \
  --env MODEL=yolov5_openvino_2021.4_6shave.blob \
  --env CONFIG=gear_yolov5.json --rm \
  --privileged \
  -v /dev/bus/usb:/dev/bus/usb \
  --device-cgroup-rule='c 189:* rmw' \
  mathugo/ofb-depthai 