# S7-Plugin für SmarthomeNG 

MIt disem Plugin kann die Kommunikation mit Siemens S7 Steuerungen(200/300/1200/1500) aufgebaut werden. Es basiert auf [Snap7](http://snap7.sourceforge.net/) und [snap7-python](https://github.com/gijzelaerr/python-snap7). Es nutzt lediglich die Client Funktionalitäten von Snap7.

Erfolgreich getestet wurde bisher: S7-1212.

Es werden Bit, Byte / Word lesen bzw. schreiben an die Steuerung unterstützt. Dabei kann auf die Prozess Ein- und Ausgänge (PE, PA) sowie auf Datenbausteine(DB), Merker(M), Timer(T) und Zähler(C) zugegriffen werden.

Das Plugin Unterstützt die Datenpunkte:

| dpt |            |bits |
| ----|------------|-----|
| 1   | bit        | 1   |
| 5   | byte       | 8   |
| 9   | word       | 16  |
| 14  | doppelwort | 32  |
