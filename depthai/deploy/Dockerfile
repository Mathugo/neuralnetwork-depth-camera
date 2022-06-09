FROM mathugo/openvino-pi
LABEL maintainer="hugo.mathh@gmail.com"
LABEL build_date="2022-06-09"
LABEL description="Perform object detection with depthai and openvino on Raspberry Pi 3 with Python3.7, Openvino 2021"

USER root
RUN apt-get update
RUN echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | tee /etc/udev/rules.d/80-movidius.rules
RUN apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install depthai 
#USER openvino
ENV PYTHONUNBUFFERED 1

ADD runtime /app/runtime
ADD models /app/models
ADD json /app/json
ADD api /app/api
ADD main.py /app/
WORKDIR /app/
CMD source /opt/intel/openvino/bin/setupvars.sh && python3 main.py --model $MODEL --config $CONFIG