#!bin/bash

sphinx-apidoc -o docs/source depthai-niryo/deploy/
cd docs && make html
