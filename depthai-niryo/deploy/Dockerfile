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
RUN git config --global http.postBuffer 1048576000
RUN git clone https://github.com/NiryoRobotics/niryo_one_ros.git
WORKDIR niryo_one_ros/niryo_one_tcp_server
RUN python3 setup.py install
WORKDIR clients/python
RUN python3 setup.py install

ADD src/runtime /app/src/runtime
ADD src/api /app/src/api
ADD src/niryo /app/src/niryo
ADD models /app/models
ADD config /app/config
ADD main.py /app/
WORKDIR /app/

CMD source /opt/intel/openvino/bin/setupvars.sh && python3 main.py --model $MODEL --config $CONFIG --mqtt_broker $MQTT_BROKER --mqtt_topic $MQTT_TOPIC