# Verschiedene Plugins für [SmarthomeNG](https://www.smarthomeng.de/)


Um eine SPS an SmarthomeNG anzuschließen gibt es mehrere Möglichkeiten. So ist es möglich, bei einer Siemens SPS über das S7 Plugin die Daten abzugreifen bzw. zu schreiben. Aber auch über Modbus TCP oder OPC Ua kann auf die SPSen von Siemens und anderen Herstellern wie z.b. Beckhoff, Xinje und andere zugegriffen werden.

## S7
stellt eine Verbindung über eine Implementierung des Siemens eigenen Protokolls her.([snap7](http://snap7.sourceforge.net/))

## ModbusTCP 
nutzt [pymodbus](https://pymodbus.readthedocs.io/en/latest/readme.html) zur Kommunikation mit jeder Art Gerät.
Getestet wurde die Kommunikation mit einer Siemens S71211C. ModbusRegsieter lt. [Siemens](https://support.industry.siemens.com/cs/document/100633819/wie-werden-bei-einem-modbus-tcp-datenaustausch-die-speicherbereiche-in-der-simatic-s7-1200-s7-1500-und-im-modbus-ger%C3%A4t-adressiert-?dti=0&lc=de-WW)
"
Funktion    | Register                           | Adresse
------------|------------------------------------|-------------
mfunction 2 | Discrete Inputs   (Eingangs-Bits)	 | 0 bis 9998
mfunction 4 | Input Register    (Eingangs-Worte) | 0 bis 9998
mfunction 5 | Coils             (Ausgangs-Bits)	 | 0 bis 9998
mfunction 6 | Holding Register  (Ausgangs-Worte) | 0 bis 65535"

## OPCua
erstellt einen OPCua Server, mit Hilfe eines OPC UA Clients können die Items gelesen und verändert werden.Es basiert auf [freeOPCua](https://github.com/FreeOpcUa)



