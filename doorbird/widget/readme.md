* This is a Widget for Smartvisu *
Place these Files in smartvisu/dropins/ Folder.
Then you can use them with:

`
{% import "doorbird.html" as doorbird %}
{{ doorbird.doorbird_history('', 'sprechanlage.live.snapshot_images', 'sprechanlage.live.doorbell_images','sprechanlage.live.motion_images', '','sprechanlage.befehl.relay1','sprechanlage.befehl.relay2', 'sprechanlage.befehl.Licht','') }}
{{ doorbird.doorbird_live('','sprechanlage.live.klingel','sprechanlage.live.bewegungsmelder', 'sprechanlage.live.live_audio', 'sprechanlage.live.live_video', 'sprechanlage.befehl.Licht','sprechanlage.befehl.Snapshot', 'sprechanlage.befehl.Relay1','sprechanlage.befehl.Relay2',  ['Nachtsicht','Snapshot','Relay1','Relay2']) }}
`
