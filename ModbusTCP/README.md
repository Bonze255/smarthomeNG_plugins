#Modbus TCP Plugin for Smarthome.py 

The Plugin is based on Smarthome.py for Communikate with a Wago/Beckhoff.. PLC.
It Read/Writes cyclical all used Registers(Items) to the PLC.
It is easy to use, like the Knx Plugin.
The Plugin is based on pymodbus, which you can found under:
https://github.com/bashwork/pymodbus

##install
<pre>
sudo apt-get install setuptools
sudo apt-get install python-dev
sudo apt-get install libevent-dev
git clone git://github.com/bashwork/pymodbus/ -b python3
sudo python3 setup.py install
</pre>

##Registerbereiche(unvollständig)
-1**Beckhoff**
-1  Beckhoff BC9100 Controller
    IN: 0
    OUT: 16384(Merkerbereich)
    (lt. Beckhoff Support ist es besser nicht direkt auf den Ausgangsbereich zuzugreifen, deshalb sollte man den Umweg über die Merker nehmen)
-2**Wago**
-1  Wago 750-342 Controller
    IN: 0
    OUT: 0
-2 Wago 750-341 Controller
    IN: 0
    OUT: 0
-3 Wago 750-842 Controller
    IN: 0
    OUT: 0
-4 Wago 750-841 Controller
    IN: 0
    OUT: 0
-5 Wago 758-870 Controller
    IN: 0
    OUT: 0
</pre>
##[plugin.conf]
<pre>
[modbus]
	class_name = modbus
	class_path = plugins.modbus
	device = 192.168.178.24		#IP adress of Modbus device
	port = 502 			#standart 502 for Modbus
	timeout = 1000 			#ms
	cycle = 2			#s
	pe_adress = 0			#start of input Registers
	pe_length = 16 			#length of the input registers
	pa_adress = 16384		#start of output Registers
	pa_length = 16	        	#length of the ouput registers
</pre>


for example:
##[item.conf]
<pre>
[beckhoff]
	name = Beckhoff PLC
    	[[outputs]]
    	name = outputs
		[[[light]]]
		name = light
		type = bool
		visu = yes
		visu_acl = rw
		modbus_on = 1
		modbus_type = bool
		modbus_byte = 16384
		modbus_bit = 0          #position in an 16bit string 16<-0
		modbus_dpt = 1
</pre>
