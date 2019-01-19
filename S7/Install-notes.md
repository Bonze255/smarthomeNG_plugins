#Installationsanweisungen folgen

sudo pip3 install snap7-python

#download and compile snap7 for rpi
wget http://sourceforge.net/projects/snap7/files/1.2.1/snap7-full-1.4.1.tar.gz/download 
tar -zxvf download
cd snap7-full-1.4.1/build/unix

#für Rpi 2/3# 
sudo make –f arm_v7_linux.mk all 
#copy compiled library to your lib directories
sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/lib/libsnap7.so
sudo cp ../bin/arm_v7-linux/libsnap7.so /usr/local/lib/libsnap7.so

#alternativ für Rpi 1# 
sudo make –f arm_v6_linux.mk all # for Rpi1
#copy compiled library to your lib directories
sudo cp ../bin/arm_v6-linux/libsnap7.so /usr/lib/libsnap7.so
sudo cp ../bin/arm_v6-linux/libsnap7.so /usr/local/lib/libsnap7.so
