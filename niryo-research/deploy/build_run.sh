docker build -t ofb-niryo .
# mount volume read only
docker run -p 127.0.0.1:80:8080/tcp  -v `pwd`:`pwd` -i -t  ofb-niryo