# Doorbird Plugin for *[SmarthomeNG](https://www.smarthomeng.de)*, 
based on https://pypi.org/project/DoorBirdPy/.
Its possible to make a snapshot from Live-Stream, switch the Relays1/2 or the Nightvision on and events like 
Doorbell, Motion.
So you can use this with knx or mqtt ....

It uses pynacl and chacha20-poly1305to encrypt the UDP Ethernet Pakets, which are listet in the requirements.txt file..

## Supported by the Plugin
* Make snapshots, when you want, and trigger them from other sources
* Get the images as array for visualisation with smarthomeNG
* Can save the images local (motion, doorbell, manual snapshot) 
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
 * DoorBird D2100E


## Widget
Save widget files to "dropins"-dir of SmartVISU
		
### Widget to show saved Pictures
add this to html Page
```
{% import "doorbird.html" as doorbird %}
{{ doorbird.doorbird_history('history', 'sprechanlage.live.snapshot_images', 'sprechanlage.live.doorbell_images', 'sprechanlage.live.motion_images', '1000', '10') }}
```		
### Widget to show Live Data
---
