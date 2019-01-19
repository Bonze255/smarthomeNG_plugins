#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################

#  Copyright 2014 Version-1    Dominik Lott        dominik.lott@tresch-automation.de
#
#  Copyright 2015 Version-2    Frank Weber                       simatic-man@web.de
#
#  Copyright 2018 Version-3    Manuel Holländer
#   - Anpassung an SmartPlugin
#   - Geschwindigkeit optimiert, Code aufgeräumt
#   - Benutzung der snap7-python eigenen Methoden
####################################################################################
#
#  This Plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  smartopenHMI is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################
#
#   VERSION - 3
#
####################################################################################
# 
import logging
import threading
import struct
import binascii
import re
import snap7
import time

from snap7.snap7types import areas
from snap7.snap7exceptions import Snap7Exception
from snap7.snap7types import S7AreaDB, S7WLBit, S7WLByte, S7WLWord, S7WLDWord, S7WLReal, S7DataItem, S7AreaMK
from snap7.util import *
import lib.connection
from lib.model.smartplugin import SmartPlugin

class S7(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"
    
    def __init__(self, smarthome, time_ga=None, date_ga=None, read_cyl_fast=1, read_cyl_slow=10, busmonitor=False, host='127.0.0.1', port=102, rack=0, slot=0):
        self._host = str(host)
        self._rack = int(rack)
        self._slot = int(slot)
        self._port = int(port)
        self._sh = smarthome
        self.gal = {}
        self.gar = {}
        self._init_ga = []
        self._cache_ga = []
        self.time_ga = time_ga
        self.date_ga = date_ga
        self.types = {'I':'PE','Q':'PA','M':'MK','C':'CT','T':'TM'}
        self.client = snap7.client.Client()
        self.logger = logging.getLogger(__name__)
        # es gibt nur 3 mögliche datentypen types
        # bool, num (int oder real), str
        #s7_dpt 
        #bit        1   = 1bit
        #byte=      5/6 = 8bit
        #wort =     9   = 16bit
        #doppelwort 14  = 32bit
        #string     16  
        #datum      11
        #uhrzeit    10
        

        try:
            self.client.connect(self._host, self._rack, self._slot, self._port)
        except Snap7Exception:
             self.logger.error("S7: Could not connect to PLC with IP: {}".format(self._host))
        finally:
            if self.client.get_connected:
                self.logger.debug("S7: CPU Status: {}".format(self.client.get_cpu_state()))
                #self.logger.debug("S7: CPU Status: {}".format(self.client.get_cpu_info()))
            else:
                try:
                    self.client.connect(self._host, self._rack, self._slot, self._port)
                except Snap7Exception:
                    self.logger.error("S7: Could not connect to PLC with IP: {}".format(self._host))

        self._lock = threading.Lock()



        #if read_cyl_fast:
        #    self._sh.scheduler.add('S7 read cycle fast', self._read_fast, prio=5, cycle=int(read_cyl_fast))
        if read_cyl_fast:
            self._sh.scheduler.add('S7 read cycle fast', self._read, prio=5, cycle=int(read_cyl_fast))

        if read_cyl_slow:
            #self._sh.scheduler.add('S7 read cycle slow', self._read_slow, prio=5, cycle=int(read_cyl_slow))
            self._sh.scheduler.add('S7 read cycle slow', self._read, prio=5, cycle=int(read_cyl_slow))

    # ----------------------------------------------------------------------------------------------
    # Daten schreiben, über SHNG bei item_Change
    # ----------------------------------------------------------------------------------------------
    def groupwrite(self, ga, payload, dpt):
        self.logger.debug("Groupwrite ga: {0}, payload:{1}, dpt:{2}".format(ga,str(payload),dpt))
        
       
        if '|' in ga:
            type, dst = ga.split('|')
            if type[0] in self.types.keys():
                area = self.types[type[0]]
        else:
            area = 'DB'
        ret_s7_num = re.findall(r'\d+', ga)   
        try:
            if dpt == '1':
                self.logger.debug("S7: Schreibe Bool")
                ret_val = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 1)
                snap7.util.set_bool(ret_val, 0, int(ret_s7_num[2]), payload)                  #modifie bit in 0. byte of bytearray        
                self.client.write_area(areas[area],int(ret_s7_num[0]), int(ret_s7_num[1]), ret_val)         #Schreibe DB / Ab / Byte
            elif dpt == '5':
                self.logger.debug("S7: Schreibe Dezimalzahl")
                if payload < 32768 and payload > -32767:
                    if area == 'DB':
                        ret_val = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 2)
                        #set payload to the bytearray
                        snap7.util.set_int(ret_val, 0, payload)                                   #set byte in 0. byte of bytearray
                    
                        self.logger.debug("S7: schreibe den Wert {0} an {3} {1}\{2}".format(payload, int(ret_s7_num[0]),int(ret_s7_num[1]), area ))
                        self.client.write_area(areas[area],int(ret_s7_num[0]), int(ret_s7_num[1]), ret_val)         #Schreibe DB / Ab / Byte
                    else:
                        ret_val = self.client.read_area(areas[area],0, int(ret_s7_num[0]), 2)
                        #set payload to the bytearray
                        snap7.util.set_int(ret_val, 0, payload)                                   #set byte in 0. byte of bytearray
                    
                        self.logger.debug("S7: schreibe den Wert {0} an {2} {1}".format(payload, int(ret_s7_num[0]),area) )
                        self.client.write_area(areas[area],0, int(ret_s7_num[0]), ret_val)         #Schreibe DB / Ab / Byte
                else:
                    self.logger.error("S7: Could not write {0}, Payload bigger than 2 Bytes!(-32767<payload<32768) {1}".format(int(ret_s7_num[0]),payload))
                    
            elif dpt == '6':
                self.logger.debug("S7: Schreibe Gleitzahl")
                ##payload to dpt
                ret_val = self.client.db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 4)
                snap7.util.set_real(ret_val, 0, payload)
                self.client.db_write(int(ret_s7_num[0]), int(ret_s7_num[1]), ret_val)         #Schreibe    DB / Ab / Byte

                
                # Schreibe String
        except Snap7Exception as e:
            self.logger.error("S7: Error writing {0} to {1} with function {3} {4}".format(payload,ret_s7_num, area, e))
        finally:
            self.logger.debug("_____________________________________________________________")
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, über SHNG bei item_Change
    # ----------------------------------------------------------------------------------------------
    def groupread(self, ga, dpt):
        self.logger.debug("S7: groupread while item is changed, ga:{0}, dpt:{1}".format(ga, dpt))

        val = 0 				#Item-Value
        src = ga				#Source-Item      (Quell-Adresse)
       
        if '|' in ga:
            type, ga = ga.split('|')
            if type[0] in self.types.keys():
                area = self.types[type[0]]
                dbnum = 0
            else:
                self.logger.warning("S7: This {0} is not a valid Area!".format(type[0]))
        else:
            area = 'DB'
            
        ret_s7_num = re.findall(r'\d+', ga)

        self.logger.debug("S7: Datenpunkt: {0}, Lesetyp {1} ".format(dpt, area))
        
        try:
                if dpt == '1':
                    #Initialisiere Bool
                    ret_val = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 1)
                    val = snap7.util.get_bool(ret_val, 0, int(ret_s7_num[2]))                     #Lese    Value aus Byte / Adresse 
                    self.logger.debug("S7: Result read one bit {0} (bool) from {1}{2}".format(val,area, ret_s7_num))
                
                elif dpt == '5':
                    #Initialisiere Dezimalzahl
                    self.logger.debug("S7: Initialisiere Dezimalzahl")
                    self.logger.debug("S7: Read one byte from {1}{2}".format(area, ret_s7_num))
                    
                    if area == 'DB':
                        self.logger.debug("S7: DB Adresse {0} / {1}".format(ret_s7_num[0], ret_s7_num[1]))
                        result = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 2) #Lese    2 DB / Ab / Byte    
                    else:
                        self.logger.debug("S7: Adresse {0} / {1} / {2}".format(ret_s7_num[0],dpt, area))
                        result = self.client.read_area(areas[area], 0, int(ret_s7_num[0]), 2) #Lese    2 DB / Ab / Byte    
                    val = snap7.util.get_int(result, 0)
                    self.logger.debug("S7: result{0}".format(val))
                    self.logger.debug("S7: Result read one byte (int)  {0} from {1}".format(val,ret_s7_num))
                    
                elif dpt == '6':
                    #Initialisiere Gleitzahl
                    self.logger.debug("S7: Initialisiere Gleitzahl")
                    self.logger.debug("S7: Adresse {0}/ {1}".format(ret_s7_num[0], ret_s7_num[1]))
                    
                    if area == "DB":
                        result = self.client.read_area(areas[area],int(ret_s7_num[0]), int(ret_s7_num[1]), 4)       #Lese    DB / Ab / Byte    
                    else:
                        self.logger.debug("S7: gleitzahl lesen 4 byte{0} {1}".format(int(ret_s7_num[0])))
                        result = self.client.read_area(areas[area], int(ret_s7_num[0]), 4)       #Lese    DB / Ab / Byte    
                        self.logger.debug("S7: {0}".format(result))
                    val = snap7.util.get_real(result, 0)

                    self.logger.debug("S7: Result read one word (real) {0} from {1}".format(val,ret_s7_num))
                
                item(val, 'S7', src, ga)
                self.logger.debug("S7: Set {3} with ga {2} ans source {1} to {0}".format(val,src,ga, item))
                
        except Snap7Exception as e:
            self.logger.warning("S7: Could not read {0} / {1} / {2} because {3}".format(src,ga, item,e))
        finally:
            self.logger.debug("_____________________________________________________________")
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, zyklisch
    # ----------------------------------------------------------------------------------------------     
    def _read(self):
        for ga in self._init_ga:
            self.logger.debug("S7: Daten lesen Zyklisch")
            self.logger.debug("S7: Adresse: " +  ga)
            val = 0 			                #Item-Value
            src = ga			                #Source-Item      (Quell-Adresse)
            dst = ga 			                #Destination-Item (Ziel-Adresse)
     
            try:
                for item in self.gal[dst]['items']:
                    ##############################################################################
                    #dst = \3     == db
                    #dst = \x\2   == byte
                    #dst = \x\x\3 == bit in byte
                    #dst = x|1\2\3 ->x = I => input
                    #                x = X => output  
                    #                x = M => Merker
                    #                x = T => Timer
                    #                x = C => Counter
                    #############################################################################
                    if '|' in dst:
                        type, dst = dst.split('|')
                        if type[0] in self.types.keys():
                            area = self.types[type[0]]
                    else:
                        area = 'DB'
                    ret_s7_num = re.findall(r'\d+', dst)

                    dpt = item.conf['s7_dpt']

                    self.logger.debug("S7: Datenpunkt: {0}, function {1}, Destination {2} ".format(dpt, area, ret_s7_num))

                    if dpt == '1':
                        #Initialisiere Bool
                        #self.logger.debug("Initialisiere Bool")
                        # good ret_val = self.client.as_db_read(int(ret_s7_num[0]), int(ret_s7_num[1]), 1)      #Lese    1 DB / Ab / Byte
                        ret_val = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 1)
                        val = snap7.util.get_bool(ret_val, 0, int(ret_s7_num[2]))                     #Lese    Value aus Byte / Adresse 
                        self.logger.debug("S7: Result read one bit {0} (bool) from {1}".format(val,ret_s7_num))
                    
                    elif dpt == '5':
                        #Initialisiere Dezimalzahl
                        self.logger.debug("S7: Initialisiere Dezimalzahl")
                        
                        if area =="DB":
                            self.logger.debug("S7: Adresse {0}/ {1}".format(ret_s7_num[0], ret_s7_num[1]))
                            result = self.client.read_area(areas[area], int(ret_s7_num[0]), int(ret_s7_num[1]), 2) #Lese    2 DB / Ab / Byte    
                        else:
                            self.logger.debug("S7: {0} {1} {2}".format(ret_s7_num[0], dpt, area))
                            self.logger.debug("S7: gleitzahl lesen 2 byte{0}".format(int(ret_s7_num[0])))
                            result = self.client.read_area(areas[area],0, int(ret_s7_num[0]), 2)       #Lese    DB / Ab / Byte    
                            self.logger.debug("S7: {0}".format(result))
                        val = snap7.util.get_int(result, 0)
                        self.logger.debug("S7: Result read one byte (int)  {0} from {1}".format(val,ret_s7_num))
                        
                    elif dpt == '6':
                        #Initialisiere Gleitzahl
                        self.logger.debug("S7: Initialisiere Gleitzahl")
                        if area == 'DB':
                            result = self.client.read_area(areas[area],int(ret_s7_num[0]), int(ret_s7_num[1]), 4)       #Lese    DB / Ab / Byte    
                        else:
                            self.logger.debug("S7: gleitzahl lesen 4 byte{0} {1} {2}".format(area, ret_s7_num[0], dst ))
                            result = self.client.read_area(areas[area], 0, int(ret_s7_num[0]), 4)       #Lese    DB / Ab / Byte    
                            self.logger.debug("S7: {0}".format(result))
                        val = snap7.util.get_real(result, 0)
                        self.logger.debug("S7: Result read one word (real) {0} from {1}".format(val,ret_s7_num))
                    elif dpt == '16':
                        #Initialisiere Gleitzahl
                        self.logger.debug("S7: Initialisiere String")
                        result = self.client.read_area(areas[area], 0, int(ret_s7_num[0]), 4)       #Lese    DB / Ab / Byte    
                        self.logger.debug("S7: {0}".format(result))
                    item(val, 'S7', src, ga)
                    self.logger.debug("S7: Set {3} with ga {2} ans source {1} to {0}".format(val,src,ga, item))
                    
            except Exception as e:
                self.logger.warning("S7: Could not read {0} / {1} / {2} because {3}".format(src,ga, item,e))
            finally:
                self.logger.debug("_____________________________________________________________")
    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.client.disconnect()
        self.client.destroy()

    def parse_item(self, item):
        if 's7_dtp' in item.conf:
            self.logger.warning("S7: Ignoring {0}: please change s7_dtp to s7_dpt.".format(item))
            return None

        if 's7_dpt' in item.conf:
            dpt = item.conf['s7_dpt']
            if dpt not in ['1','5','9','14']:
                self.logger.warning("S7: This is not a valid dpt.{0} {1}.".format(item, dpt))
            if '|' not in dpt:
                self.logger.info("S7: No Function (I,X, M, C, T) for {} given, using default DB ".format(item))
        else:
            return None

        if 's7_read_s' in item.conf:
            ga = item.conf['s7_read_s']
            self.logger.debug("S7: {0} listen on and init with {1}".format(item, ga))

            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._init_ga.append(ga)

        if 's7_read_f' in item.conf:
            ga = item.conf['s7_read_f']
            self.logger.debug("S7: {0} listen on and init with {1}".format(item, ga))

            if not ga in self.gal:
                self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

            else:
                if not item in self.gal[ga]['items']:
                    self.gal[ga]['items'].append(item)
            self._init_ga.append(ga)

        if 's7_send' in item.conf:
            if isinstance(item.conf['s7_send'], str):
                item.conf['s7_send'] = [item.conf['s7_send'], ]

        if's7_send' in item.conf:
            return self.update_item_send
        return None


        if 's7_read' in item.conf:
            return self.update_item_read
        return None

        if 's7_listen' in item.conf:
            s7_listen = item.conf['s7_listen']
            if isinstance(s7_listen, str):
                s7_listen = [s7_listen, ]
            for ga in s7_listen:
                logger.debug("S7: {0} listen on {1}".format(item, ga))

                if not ga in self.gal:
                    self.gal[ga] = {'dpt': dpt, 'items': [item], 'logics': []}

                else:
                    if not item in self.gal[ga]['items']:
                        self.gal[ga]['items'].append(item)

    def update_item_send(self, item, caller=None, source=None, dest=None):
        if caller != 'S7':
            if 's7_send' in item.conf:
                if self.client.get_connected:
                    for ga in item.conf['s7_send']:
                        self.groupwrite(ga, item(), item.conf['s7_dpt'])
                        self.logger.debug("S7: Schreibe {0} auf {1}".format(item(), ga))

    def update_item_read(self, item, caller=None, source=None, dest=None):
        if self.client.get_connected:
            if 's7_status' in item.conf:
                for ga in item.conf['s7_status']:  # send status update
                    if ga != dest:
                        self.groupread(ga, item.conf['s7_dpt'])
                        self.logger.debug("S7: Lese {0}".format(ga))
