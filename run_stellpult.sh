#!/bin/bash
#DISPLAY=:0.1
#export DISPLAY
set -x
echo $DISPLAY
cd ~pi/projects/run/stellpult
python3 -V
#xhost +
#sudo /bin/bash -c "xauth merge /home/pi/.Xauthority; python3 Stellpult_Grafik.py "
sudo /bin/bash -c "python3 Stellpult_Grafik.py"
