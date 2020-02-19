# Doorbird plugin for smarthomeng, 
it based on https://pypi.org/project/DoorBirdPy/. Its possible to make a snapshot from Live-Stream, switch the Relays1/2 or the Nightvision on/off and get the events(doorbell, motion) from it. So you can use this with knx or mqtt ....
It uses pycryptodome and  chacha20-poly1305to encrypt the UDP Ethernet Pakets.

## Supported by the Plugin
* Make snapshots
* Get the images as array for visualisation with smarthomeNG
* Get Motion/Doorbell Events

## Supported from doorbirdpy
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
