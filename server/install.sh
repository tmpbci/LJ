#!/bin/bash
sudo apt upgrade
sudo apt install htop
sudo apt install syncthing
#sudo apt install python-pip 
sudo apt install python3-pip 
sudo apt install git
sudo apt install redis-server
sudo apt install screen 
sudo apt install tmux
#pip install numpy
#pip install scipy
#pip install python-rtmidi
#pip install mido
pip3 install scipy
pip3 install numpy
#pip install pygame==1.9.2
#pip3 install pygame==1.9.2
pip3 install redis
pip3 install pysimpledmx 
pip3 install DMXEnttecPro
sudo apt install libasound2-dev
sudo apt install libjack-dev
pip3 install python-rtmidi 
pip3 install mido
sudo apt install nginx
sudo apt install supervisor  
sudo apt install ssh
sudo cp syncthing.conf to /etc/supervisor/conf.d/
git clone https://github.com/ptone/pyosc --depth 1 /tmp/pyosc && cd /tmp/pyosc && sudo ./setup.py install 
cd /tmp
sudo apt install portaudio19-dev
sudo apt install cmake
git clone https://github.com/Ableton/link.git
cd link
git submodule update --init --recursive
mkdir build
cd build
cmake ..
cmake --build .
cd /tmp/
git clone --recursive https://github.com/gonzaloflirt/link-python.git
cd link-python
mkdir build
cd build
cmake ..
cmake --build .
