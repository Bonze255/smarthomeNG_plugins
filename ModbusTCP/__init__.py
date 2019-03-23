#!/usr/bin/env python3
####################################################################################################
#MODBUS TCP
#This Plugin use MODBUS TCPn 
#it is based on the "pymodbus" lib  for Python #
#
#by  Manuel Holländer
####################################################################################################  

import time
import logging
import threading

from pymodbus.client.sync import ModbusTcpClient as ModbusClient
from pymodbus.constants import Endian
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.payload import BinaryPayloadBuilder


class ModbusException(Exception):
    pass


from lib.model.smartplugin import SmartPlugin

class ModbusTCP(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"

####################################################################################################
#
#
#
#
#
####################################################################################################  
    def __init__(self, smarthome, host, timeout=10, port=502, cycle=5, byteorder='big', wordorder='little' ):
        ##Initialdaten aus Plugin.conf
        self._sh = smarthome
        self._items = {}
        self.timeout = float(timeout)
        self._device = str(host)
        self.port = int(port)
        self.cycle = int(cycle)
        self._unit = 0x1
        self.logger = logging.getLogger(__name__)
        ######################################
        self._adresses = []
        self.fail = False
        #1: 	bool						0...1
        #5: 	8-bit signed value			0...255
        #5.001: 8-bit unsigned value		0...100
        #6: 	8-bit signed value			-128...127
        #7: 	16-bit unsigned value		0...65535
        #8: 	16-bit signed value			-32768...32767
        #9: 	floating point 				-671088,64 - 670760,96
        if byteorder =='big':
            self.byteorder = Endian.Big
        else:
            self.byteorder = Endian.Little
        if wordorder =='big':
            self.wordorder = Endian.Big
        else:
            self.wordorder = Endian.Little
        

        if cycle:
            self._sh.scheduler.add('ModbusTCP: read cycle', self._read, prio=5, cycle=self.cycle)
        
        self.connect()
        self._lock = threading.Lock()
        
    def run(self):##plugin starten
        self.alive = True
        
    def stop(self):##plugin stoppen
        self.alive = False
        #self.client.disconnect()
        self.client.close()
        self.logger.info('ModbusTCP: Stopped!')

    def parse_logic(self, logic):##nicht benoetigt
        pass
        
    def connect(self):
        
        try:
            #if self.device is not None:
            self.client = ModbusClient(self._device, self.port)
            #self.client.connect()
            #self.connected = True
            self.logger.info('ModbusTCP: Connected to {0}'.format(self._device))
            self.fail = False
        except Exception as e:
            if self.fail == False:
                self.logger.error('ModbusTCP: Could not connect to : {0}, {1]'.format(self._device, e))
            self.fail = True
####################################################################################################
#Items beim start überprüfen, auf modbus_on = 1
####################################################################################################
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'modbus_function'):
            mfunction = item.conf['modbus_function']
            #1 Read Coil Status         1bit
            #2 Read Input Status        16bit
            #3 Read Holding Registers   16bit
            #4 Read Input Registers     16bit
            #5 Force Single Coil        1bit
            #6 Preset Single Register   16bit
            if mfunction not in ['1','2','3','4','5','6']:
                self.logger.warning("ModbusTCP: This is not a valid Modbus function.{0} {1}.".format(item, mfunction))
                pass
       
            if self.has_iattr(item.conf, 'modbus_read'):
                madress = item.conf['modbus_read']
                self.logger.debug("ModbusTCP: {0} - read from {2} and mfunction {1}".format(item,mfunction, madress))
                self._adresses.append({'mfunction': int(mfunction), 'madress': int(madress), 'item': item})
                return self.update_item
                
            if self.has_iattr(item.conf, 'modbus_write'):
                madress = item.conf['modbus_write']
                mfunction = item.conf['modbus_function']
                self.logger.debug("ModbusTCP: {0} - write to {1} and mfunction{2}".format(item, madress,mfunction))
                return self.update_item
            
        #else:
        #    self.logger.warning("ModbusTCP: Modbus Function is mandatory!{0}".format(item))
        #    return None
####################################################################################################        
##Item has changed, called by SmarthomeNG
####################################################################################################  
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'ModbusTCP':
            value = int(item())
            mfunction = int(item.conf['modbus_function'])
            if self.has_iattr(item.conf, 'modbus_write'):
                madress = int(item.conf['modbus_write'])
                try:
                    #if self.client._connected:
                    
                    if mfunction == 5:
                        #write_single_coil(bit_addr, bit_value)
                        val = self.client.write_coil(madress, value, unit=self._unit)
                        self.logger.debug('MODBUSTCP: Write on {0} with function{1} value {2}'.format(madress, mfunction, value))
                    elif mfunction == 6:
                        #write_single_register(reg_addr, reg_value)
                        val = self.client.write_register(madress, value, unit=self._unit)
                        self.logger.debug('MODBUSTCP: Write on {0} with function{1} value {2}'.format(madress, mfunction, value))
                    elif mfunction == 15:
                        #write_multiple_coils(reg_addr, reg_value)
                        bitarray = self.client.get_bits_from_int(value, val_size=16, unit=self._unit)
                        val = self.client.write_multiple_coils(madress, bitarray, unit=self._unit)
                    elif mfunction == 16:
                        #write_multiple_registers(regs_addr, regs_value)
                        val = self.client.write_multiple_registers(madress, value, unit=self._unit)
                    
                    #if val.function_code > 0x80:
                    #    self.logger.error('MODBUSTCP: Could not write on {0} with function{1}, because Errorcode{2}'.format(madress, mfunction, val))
                    #else:
                    #    self.logger.error('MODBUSTCP: Client failure, not connected')
                except Exception as e:
                    self.logger.error('MODBUSTCP: ERROR; Could not write an OutWord, because {}'.format(e))
                    

####################################################################################################
#Read all Items, who are in self._adresses, called by Scheduler
####################################################################################################  
    def _read(self):
        self._lock.acquire() 
        try:
            #if self.client._connected:
            for adress in self._adresses:
                #self.logger.debug('MODBUSTCP: {0}'.format(adress))
                item = adress['item']
                mfunction = adress['mfunction']
                madress = adress['madress']
                #type = item.conf['type']
                if self.has_iattr(item.conf, 'modbus_format'):
                    mformat = item.conf['modbus_format']
                else:
                    mformat = 'raw'
              
                
                if mfunction == 1:#Read Coil Status => Status der Ausgänge des MODBUS TCP Servers! ,bitorientiert 
                    val = self.client.read_coils(madress, 1, unit=self._unit)
                    val = val.bits[0]
                    self.logger.debug('MODBUSTCP: Read from adress {0}, function {1}, item {2} = {3}'.format(madress, mfunction, item, val))
                # #Read Input Status 0> STatus der Eingänge    
                elif mfunction == 2: #Read Discrete Inputs  => Status der Eingänge des MODBUS TCP Servers!, bitorientiert 
                # #read_discrete_inputs(bit_addr, bit_nb=1)
                    val = self.client.read_discrete_inputs(madress, 1, unit=self._unit)
                    val = val.bits[0]
                    self.logger.debug('MODBUSTCP: Read from adress {0}, function {1}, item {2} = {3}'.format(madress, mfunction, item, val))
                elif mfunction == 3:#Read Holding Registers  => Status der Merker des MODBUS TCP Servers!, byteoriertiert 
                # #read_holding_registers(reg_addr, reg_nb=1)
                    #pass
                    val = self.client.read_holding_registers(madress, 1, unit=self._unit)
                    #val = val.registers[0]
                elif mfunction == 4:#Read INput Registers  => Status der Eingänge des MODBUS TCP Servers!, byteoriertiert 
                # #read_input_registers(reg_addr, reg_nb=1)
                    
                    
                    if '8' in mformat:
                        size = 1
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        if 'uint' in mformat:
                            val = decoder.decode_8bit_uint()
                        else:
                            val = decoder.decode_8bit_int()
                    elif 'bits' in mformat:
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        val = decoder.decode_bits()
                    elif '16'in mformat :
                        size = 1
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        if 'uint' in mformat:
                            val = decoder.decode_16bit_uint()
                        else:
                            val = decoder.decode_16bit_int()
                        
                    elif '32' in mformat:
                        size = 2
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        if 'uint' in mformat:
                            val = decoder.decode_32bit_uint()
                        else:
                            val = decoder.decode_32bit_int()
                    elif '64' in mformat:
                        size = 4
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        if 'uint' in mformat:
                            val = decoder.decode_64bit_uint()
                        else:
                            val = decoder.decode_64bit_int()
                    elif 'raw' in mformat:
                        value = self.client.read_input_registers(madress, size, unit=self._unit)
                        decoder = BinaryPayloadDecoder.fromRegisters(value.registers, byteorder=self.byteorder, wordorder=self.wordorder)
                        val = decoder.skip_bytes(8)
                    else:
                        val = 0
                    #decoded = {
                            # 'string': decoder.decode_string(8),
                            # 'bits': decoder.decode_bits(),
                            #'8int': decoder.decode_8bit_int(),
                            # '8uint': decoder.decode_8bit_uint(),
                            #'16int': decoder.decode_16bit_int(),
                            # '16uint': decoder.decode_16bit_uint(),
                            #'32int': decoder.decode_32bit_int(),
                            # '32uint': decoder.decode_32bit_uint(),
                            # '32float': decoder.decode_32bit_float(),

                            # '64int': decoder.decode_64bit_int(),
                            # '64uint': decoder.decode_64bit_uint(),
                            # 'raw': decoder.skip_bytes(8),
                            # '64float': decoder.decode_64bit_float(),
                    #}
                    
                if value == None:
                    self.logger.error('MODBUSTCP: Could not read from {0} with function {1}'.format(madress, mfunction))
                else:
                    #val = decoded[mformat]
                    self.logger.debug('MODBUSTCP: Read from adress {0}, with size {1},function {2} item {3} = {4}'.format(madress, size, mfunction, item, val))    
                    item(val, 'ModbusTCP')
        except Exception as e:
            self.logger.error('MODBUSTCP: Could not read from adress {0} with function {1}, because {2}'.format(madress, mfunction,e))
        finally:
            self._lock.release()     
####################################################################################################
#wandelt str in binary ohne führendes 0b
#und invertiert auf wunsch das Ergebnis!
#
#
#
####################################################################################################  

    def toBinary2(self, n, invert = 1):##
        byte = '{:08b}'.format(n)
         
        i = int(16)-len(byte)
        ausgabe = ""
        for x in range(0,i):
            ausgabe = "0"+ausgabe
        ausgabe = ausgabe+byte
        if invert == 1:#invertieren
            ausgabe = ausgabe[::-1]
        return ausgabe
        
    def toBinary(self, n, invert = 0):##
        byte = '{:08b}'.format(n)
        if invert == 1:#invertieren
            byte = byte[::-1] 
        ausgabe = []
        if byte == '00000000':
            ausgabe.append('00000000')
            ausgabe.append('00000000')
        elif byte < '256' :
            ausgabe.append(byte[0:8])
            ausgabe.append('00000000')
        else:
            ausgabe.append(byte[0:8])
            ausgabe.append(byte[8:17])   
        return ausgabe 

    def de5001(self, value):                                                                        #8bit 0-100 auf 0-255 normieren
        if value > 255:
            value = 255
        elif value < 0:
            value = 0
        return int(round(value*2.55))
    def en5001(self, value):                                                                        #8bit auf 0-100 normieren
        if value > 255:
            value = 255
        elif value < 0:
            value = 0
        return (round((value/2.55), 2))
####################################################################################################
#Helper FUnction to split modbus register
####################################################################################################      
    def split_ga(self, ga):
        if '|' in ga:
            type, dst = ga.split('|')
            if type in self.types.keys():
                area = self.types[type]
            else:
                area = 'DB'
        else:
            area = 'DB'
        s7area = areas[area]
        
        #split db\byte\bit    
        ret_s7_num = re.findall(r'\d+', ga)
        
        if area == 'DB': #db = 3  []
            if len(ret_s7_num) > 2:
                #dbnum, byte,bit = ret_s7_num
                dbnum = int(ret_s7_num[0])
                byte = int(ret_s7_num[1])
                bit = int(ret_s7_num[2])
            else:
                dbnum = int(ret_s7_num[0])
                byte = int(ret_s7_num[1])
                bit = 0
        else:# other only 2 
            dbnum = 0
            if len(ret_s7_num) > 1:
                byte = int(ret_s7_num[0])
                bit = int(ret_s7_num[1])
            else:
                byte = int(ret_s7_num[0])
                bit = 0
                
        self.logger.debug("S7: split_ga {0}".format([s7area, dbnum, byte, bit]))
        return [s7area, dbnum, byte, bit]
