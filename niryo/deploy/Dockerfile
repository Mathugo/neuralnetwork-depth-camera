#FROM ubuntu:kinetic
#FROM ros:foxy
FROM ubuntu:18.04

RUN apt-get update 
RUN apt-get install -y git python3-dev python3-pip 
RUN apt-get install -y gnutls-bin 

#dpkg catkin
#python-catkin-pkg

RUN pip3 install jsonpickle catkin_pkg setuptools
RUN pip3 install Cython pyparsing numpy 
RUN git config --global http.postBuffer 1048576000

RUN git clone https://github.com/NiryoRobotics/niryo_one_ros.git
WORKDIR niryo_one_ros
WORKDIR niryo_one_tcp_server
RUN python3 setup.py install
WORKDIR clients/python
RUN python3 setup.py install

WORKDIR /app
ADD main.py /app/
ADD niryo.py /app/
CMD python3 main.py



