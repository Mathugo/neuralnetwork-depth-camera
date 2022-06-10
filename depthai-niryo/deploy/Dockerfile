FROM mathugo/openvino-pi
LABEL maintainer="hugo.mathh@gmail.com"
LABEL build_date="2022-06-09"
LABEL description="Perform object detection with depthai and openvino on Raspberry Pi 3 with Python3.7, Openvino 2021"

# depthai 
USER root
RUN apt-get update
RUN echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | tee /etc/udev/rules.d/80-movidius.rules
RUN apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx 
RUN python3 -m pip install --upgrade pip
ADD requirements.txt /app/
RUN python3 -m pip install -r /app/requirements.txt
ENV PYTHONUNBUFFERED 1

# niryo
RUN apt-get install git python-rospy
ADD src/niryo /app/src/niryo
ADD build/python_tcp_client /app/src/niryo/python_tcp_client
WORKDIR /app/src/niryo/python_tcp_client
RUN python3 setup.py install
RUN mv /app/src/niryo/python_tcp_client/niryo_one_tcp_client/ /app/src/niryo/niryo_one_tcp_client


ADD src/runtime /app/src/runtime
ADD src/api /app/src/api
ADD src/mqtt /app/src/mqtt
ADD models /app/models
ADD config /app/config
ADD main.py /app/

WORKDIR /app/
# tcp port for niryo
EXPOSE 40001

#CMD python3 main.py --model $MODEL --config $CONFIG --mqtt_broker $MQTT_BROKER --mqtt_topic $MQTT_TOPIC