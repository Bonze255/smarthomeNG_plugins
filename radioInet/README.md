## Plugin for smarthomeNG to Control a Busch & Jäger  Radio INet 8216U

#### Version 1.0.0

This plugin can be control a Busch und Jäger Radio iNet 8216U over HTTP Requests and UDP Commands. Based on the Thread from fhem (https://forum.fhem.de/index.php?topic=47240.0)

## Support
Support is provided trough the support thread within the smarthomeNG forum: [Smarthome.py](https://knx-user-forum.de/forum/supportforen/smarthome-py)

## Change History

### Changes Since version 1.0.0

### Requirements
- socket
- re
- json

## Configuration

### plugin.conf

Use the plugin configuration to configure the plugin. 

```yaml
# for etc/plugin.yaml configuration file:
radioinet:
    class_name: RadioInet
    class_path: plugins.radio_inet
    device: xxx.xxx.xxx.xxx
    cycle: 10
```

#### item_subtree

**```item_subtree```** defines the part of the item-tree which the plugin searches during data updates for the **```radio```** attribute. 

If **```item_subtree```** is not defined or empty, the whole item-tree is searched, which creates unnecessary overhead vor SmartHomeNG.

If you are going to configure multiple instances of the plugin to get the weather report for multiple locations, you have to specify the parameter, or you will get da data mix up. 

The subtrees defined by **`item_subtree`** for the different instances must not intersect!

#### cycle

### items configuration

#### radio
        DISCOVER: Nach Radio suchen. Als UDP-Broadcast sollte das alle Radios im Subnetz zurückmelden.
        GET: Wert auslesen, der folgende Parameter sagt, was gelesen werden soll:
            POWER_STATUS
            INFO_BLOCK
            ALARM_STATUS
            VOLUME
            PLAYING_MODE
            ALL_STATION_INFO
            TUNEIN_PARTNER_ID
        SET: Wert setzen/ändern. Hier gibt es folgende Möglichkeiten:
            RADIO_ON
            RADIO_OFF
            VOLUME_ABSOLUTE:<volume>
            VOLUME_INC
            VOLUME_DEC
            VOLUME_MUTE
            VOLUME_UNMUTE
            ALARM_OFF
            ALARM_SNOOZE
            ALARM:HH:<hour>:MM:<minute>:ONOFF:0|1:STATION:<station number [1-8]>
        PLAY: Abspielen.
            STATION:<station number [1-8]>
            UPNP
            AUX
            TUNEIN_INIT (scheint mir unnötig zu sein)
            TUNEIN_PLAY. Dieser benötigt zwei weitere Parameter (eigene Zeilen, kein Quoting nötig):
            URL:<url>
            TEXT:<name> (wird im Display angezeigt)
        SAVE: Programm speichern
            STATION
            CHANNEL:<station number [1-8]>
            NAME:<text>
            URL:<url>
            TUNEIN_FAVORITE (Aktuelle URL als TuneIn-Favorite hinterlegen)
        REMOVE: hier gibt es nur eine Option.
            TUNEIN_FAVORITE
        RESET_BLOCK: Reset (?)

    available HTTP Commands:
        Read / Write complete  Configuration
        Read / Write Stationlist
        Set Play/Volume/ ...

### value
The items can have a default value, set by using the ```value``` attribute. This attribute is not plugin specific. The default values are used, if the weather station you selected does not send data for the selected matchstring. The following example defines default values for items, which are not supported by all weather stations.


### Example: items.yaml
Example configuration of an item-subtree for the  plugin in yaml-format:

```YAML
        radio:
            on: 
                type: bool
                visu_acl: rw
                radio: "on"
            play:
                type: bool
                visu_acl: rw
                radio: "play"
            next:
                type: bool
                visu_acl: rw
                radio: "next"
            rew:
                type: bool
                visu_acl: rw
                radio: "rew"
            stop:
                type: bool
                visu_acl: rw
                radio: "stop"
            title:
                type: str
                visu_acl: rw
                radio: "--"
            vol:
                type: num
                visu_acl: rw
                radio: "vo"
                plus:
                    type: num
                    visu_acl: rw
                    radio: "vp"
                minus:
                    type: num
                    visu_acl: rw
                    radio: "vm"
                mute:
                    type: bool
                    visu_acl: rw
                    radio: "mute"
            station1:
                type: str
                visu_acl: rw
                radio: "n1"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s1"
                play:
                    type: bool
                    radio: "p1"
            station2:
                type: str
                visu_acl: rw
                radio: "n2"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s2"
                play:
                    type: bool
                    radio: "p2"
            station3:
                type: str
                visu_acl: rw
                radio: "n3"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s3"
                play:
                    type: bool
                    radio: 'p3'
            station4:
                type: str
                visu_acl: rw
                radio: "n4"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s4"
                play:
                    type: bool
                    radio: "p4"
            station5:
                type: str
                visu_acl: rw
                radio: "n5"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s5"
                play:
                    type: bool
                    radio: "p5"
            station6:
                type: str
                visu_acl: rw
                radio: "n6"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s6"
                play:
                    type: bool
                    radio: "p6"
            station7:
                type: str
                visu_acl: rw
                radio: "n7"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s7"
                play:
                    type: bool
                    radio: "p7"
            station8:
                type: str
                visu_acl: rw
                radio: "n8"
                url:
                    type: str
                    visu_acl: rw
                    radio: "s8"
                play:
                    type: bool
                    radio: "p8"
            config:
                helligkeit:
                    type: num
                    radio: "bb"
                modus:
                    type: num
                    radio: "bl"
                alarm:
                    status:
                        type: bool
                        radio: "ea"
                    stunden:
                        type: num
                        radio: "ah"
                    minuten:
                        type: num
                        radio: "am"
                timer:
                    status:
                        type: num
                        radio: "et"
                    minuten:
                        type: num
                        radio: "st"
                sleeptimer:
                    status:
                        type: num
                        radio: "es"
                    minuten: 
                        type: num
                        radio: "ss"
                    

```


### logic.yaml

No logic configuration implemented.

## Methods / Functions

No methods or functions are implemented.

