from python:3.7-alpine

ADD requirements.txt /
RUN python3 -m pip install -r /requirements.txt

ADD build/python_tcp_client /app/build/python_tcp_client
WORKDIR /app/build/python_tcp_client
RUN python3 setup.py install

ADD src/niryo /app/src/niryo

EXPOSE 40001
#ENTRYPOINT ["/bin/bash", "-l", "-c"]
#CMD ["./main.py"]