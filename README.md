# Neural Network for Depth AI and Niryo robotic arm 

<!-- ABOUT THE PROJECT -->
## About The Project
Grab dynamicaly objects on a conveyor using Yolov5, depth sensing and NiryoOne robotic arm. 

The Docker image can be found at : [mathugo/ofb-depthai](https://hub.docker.com/r/mathugo/ofb-depthai)

The base image for openvino2021 working on raspbian on NiryoOne : [mathugo/openvino-pi](https://hub.docker.com/r/mathugo/openvino-pi)

### Built With

* [Python](https://www.python.org/)
* [Docker](https://www.docker.com/)
* [Depthai](https://docs.luxonis.com/en/latest/)
* [FastAPI](https://fastapi.tiangolo.com/)


## Getting Started

### Dependencies

* Docker

### File structure

```text
neuralnetwork-depth-camera/
└── depthai-niryo/
    ├── base_images/
    ├── deploy/
    │   ├── build_run.sh
    │   ├── Dockerfile
    │   ├── ...
    │   └── src/
    ├── research/
    └── docs/ 

```

### Setting environment
Environment variables can be set in `build_run.sh` according to the *docs*.

### Build image and start client
```
bash build_run.sh
```
This might take a while since Docker is pulling base images and building all necessary *Python* packages and apt libs. 

If you want to run directly the image without building : 
```
bash build_run.sh --run
```

## Authors

Contributors names and contact info

Hugo Math [@mathugo](https://hugomath.com/)


