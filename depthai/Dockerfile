FROM balenalib/rpi-raspbian:buster
LABEL maintainer="hugo.mathh@gmail.com"
LABEL build_date="2022-06-09"
LABEL description="Intel® Distribution of OpenVINO™ Toolkit for Raspberry Pi, Python3.7, Openvino 2021"

ARG DOWNLOAD_LINK=https://download.01.org/opencv/2021/openvinotoolkit/2021.2/l_openvino_toolkit_runtime_raspbian_p_2021.2.185.tgz
ARG INSTALL_DIR=/opt/intel/openvino 

RUN apt-get update && apt-get install -y --no-install-recommends \
   apt-utils \
   automake \
   cmake \
   cpio \
   gcc \
   g++ \
   libatlas-base-dev \
   libstdc++6 \
   libtool \
   libusb-1.0.0-dev \
   lsb-release \
   make \
   python3-pip \
   python3-numpy \
   python3-scipy \
   libgtk-3-0 \
   pkg-config \
   libavcodec-dev \
   libavformat-dev \
   libswscale-dev \
   sudo \
   udev \
   wget && \
rm -rf /var/lib/apt/lists/*

RUN mkdir -p $INSTALL_DIR && cd $INSTALL_DIR && \
   wget -c $DOWNLOAD_LINK && \
   tar xf l_openvino_toolkit_runtime_raspbian_p*.tgz --strip 1 -C $INSTALL_DIR
# add USB rules
RUN sudo usermod -a -G users "$(whoami)" && \
   /bin/bash -c "source $INSTALL_DIR/bin/setupvars.sh && \
   sh $INSTALL_DIR/install_dependencies/install_NCS_udev_rules.sh"
# build Object Detection sample
RUN echo "source /opt/intel/openvino/bin/setupvars.sh" >> ~/.bashrc 
