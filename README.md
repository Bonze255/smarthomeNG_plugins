# Verschiedene Plugins für [SmarthomeNG](https://www.smarthomeng.de/)


Um eine SPS an SmarthomeNG anzuschließen gibt es mehrere Möglichkeiten. So ist es möglich, bei einer Siemens SPS über das S7 Plugin die Daten abzugreifen bzw. zu schreiben. Aber auch über Modbus TCP oder OPC Ua kann auf die SPSen von Siemens und anderen Herstellern wie z.b. Beckhoff, Xinje und andere zugegriffen werden.

## S7
stellt eine Verbindung über eine Implementierung des Siemens eigenen Protokolls her.([snap7](http://snap7.sourceforge.net/))

## ModbusTCP 
nutzt [pymodbus](https://pymodbus.readthedocs.io/en/latest/readme.html) zur KOmmunikation mit jeder Art Gerät.

## OPCua
erstellt einen OPCua Server, mit Hilfe eines OPC UA Clients können die Items gelesen und verändert werden.Es basiert auf [freeOPCua](https://github.com/FreeOpcUa)



