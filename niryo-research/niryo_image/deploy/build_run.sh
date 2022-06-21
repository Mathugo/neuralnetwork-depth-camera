sudo docker build -t mathugo/ofb-niryo .
sudo docker run --rm -it -P mathugo/ofb-niryo \
    --env MQTT_BROKER="test.fr" \
    --env NIRYO_IP="192.168.1.23"
