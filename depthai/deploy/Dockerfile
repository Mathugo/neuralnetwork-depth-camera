FROM openvino/ubuntu18_dev:2021.4
USER root
RUN apt-get update
RUN apt-get install -y python3 python3-pip udev git

RUN echo 'SUBSYSTEM=="usb", ATTRS{idVendor}=="03e7", MODE="0666"' | tee /etc/udev/rules.d/80-movidius.rules
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev
RUN apt-get install -y ffmpeg libsm6 libxext6 libgl1-mesa-glx
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install depthai openvino_dev==2021.4.2 blobconverter
USER openvino
ENV PYTHONUNBUFFERED 1

ADD main.py /app/
ADD models /app/
ADD json /app/
WORKDIR /app/
CMD source /opt/intel/openvino/bin/setupvars.sh && python3 main.py --model $MODEL --config $CONFIG