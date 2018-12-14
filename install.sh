#!/bin/bash
sudo apt install python-pip 
sudo apt install git
pip uninstall serial 
pip uninstall rtmidi
pip install libasound2-dev python-dev libpython-dev libjack-dev
pip install pysimpledmx
pip install numpy
pip install scipy
pip install mido
pip install python-rtmidi 
git clone https://github.com/ptone/pyosc --depth 1 /tmp/pyosc && cd /tmp/pyosc && sudo ./setup.py install 
pip install pyserial
pip install redis



