# Xiaomi Vacuum Robot Plugin for SmarthomeNG
Das Plugin basiert auf der [python-miio](https://github.com/rytilahti/python-miio) Bibliothek. Das Plugin bzw python-miio benötigt den Kommunikationstoken des Roboters. 

- [Bitte der Installationsanweisung von python-miio folgen](https://python-miio.readthedocs.io/en/latest/discovery.html#installation)
- anschließend Xiaomi_vac nach smarthomeNG/plugins kopieren
- Folgendes zur etc/plugin.yaml hinzufügen

    ```Roboter:
    class_name: Robvac
    class_path: plugins.xiaomi_vac
    ip: '192.XXX.XXX.XXX'
    token: 'euerToken'
    read_cyl: 45
    ```
    
- Um die Verbindung zu überprüfen, kann in der Kommandozeile nach der Installation mit 

```export MIROBO_IP=192.xxx.xxx.xxx
   export MIROBO_TOKEN=euerToken
```
   
- und anschließendem

```mirobo```

    die basics abgefragt werden.


## Funktionen

folgende Werte/Funktionen können vom Saugroboter ausgelesen bzw. gestartet werden:
- Start
- Stop/ zur Ladestation fahren
- Pause
- Finden
- Spotreinigung
- Lüftergesschwindigkeit ändern
- Lautstärke ansage ändern

- gerenigte Fläche
- Reinigungszeit
- Status
- Zustand
- Fehlercode

uvm.
