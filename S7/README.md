# S7-Plugin für SmarthomeNG 

Zur Kommunikation mit Siemens S7 Steuerungen(200/300/1200/1500). Es basiert auf [Snap7](http://snap7.sourceforge.net/) und [snap7-python](https://github.com/gijzelaerr/python-snap7).Es nutzt lediglich die Client Funktionalitäten von Snap7.

Erfolgreich getestet wurde bisher: S7-1212.

Es werden Bit, Byte und Word lesen bzw. schreiben an die Steuerung unterstützt. Dabei kann auf die Prozess Ein- und Ausgänge (PE, PA) sowie auf Datenbausteine(DB), Merker(M), Timer(T) und Zähler(C) zugegriffen werden.

Das Plugin Unterstützt die Datenpunkte:<br>
| dpt |            |bits |<br>
|---: |:----      :|---: |<br>
|  1  | bit        | 1   |<br>
|  5  | byte       | 8   |<br>
|  9  | word       | 16  |<br>
|  14 | doppelwort | 32  |<br>
