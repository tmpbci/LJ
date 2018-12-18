#!/bin/bash
sudo apt install python-pip 
sudo apt install git
sudo apt install redis
pip install numpy
pip install scipy
git clone https://github.com/ptone/pyosc --depth 1 /tmp/pyosc && cd /tmp/pyosc && sudo ./setup.py install 
pip install redis



