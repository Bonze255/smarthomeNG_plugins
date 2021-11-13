# Doorbird plugin for *[SmarthomeNG](https://www.smarthomeng.de)*, 
based on https://pypi.org/project/DoorBirdPy/.
Its possible to make a snapshot from Live-Stream, switch the Relays1/2 or the Nightvision on and get the events(doorbell, motion).
So you can use this with knx or mqtt ....
It uses pynacl and chacha20-poly1305to encrypt the UDP Ethernet Pakets.

## Supported by the Plugin
* Make snapshots, when you want, and trigger them from other sources
* Get the images as array for visualisation with smarthomeNG
* Can save the images local (moton, doorbell, manual snapshot) 
* Get Motion/Doorbell Events from UDP Broadcasts, so you can trigger and link all actions you want with *[SmarthomeNG](https://www.smarthomeng.de)*
* So this Plugin can used, when you need a doorbird A1061 or A1081, because you can used any KNX Hardware instead

## Supported from doorbirdpy package
* get the URLs for
  * Live video request
  * Live image request
  * Open door/other relays
  * Light on
  * History image requests
  * Schedule requests
  * Favorites requests
  * Check request
  * Info request
  * RTSP

## all functions are available with *[SmarthomeNG](https://www.smarthomeng.de)* out of the box
## Tested with 
 * DoorBird D2101V