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
#   - Reduzierung auf 1 Scheduler
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

#import lib.connection
from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class S7(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"
    
    def __init__(self, smarthome, time_ga=None, date_ga=None, read_cyl=1, busmonitor=False, host='127.0.0.1', port=102, rack=0, slot=0):
        self._host = str(host)
        self._rack = int(rack)
        self._slot = int(slot)
        self._port = int(port)
        self._cycle = int(read_cyl)
        self._sh = smarthome
        self.gal = {}
        self.time_ga = time_ga
        self.date_ga = date_ga
        self.types = {'I':'PE','Q':'PA','M':'MK','C':'CT','T':'TM'}
        self.client_read = snap7.client.Client()
        self.client_write = snap7.client.Client()
        self.logger = logging.getLogger(__name__)
        self.stop_time_read = 0
        self.start_time_read = 0
        self.start_time_write = 0
        self.stop_time_write = 0
        # es gibt nur 3 mögliche datentypen types
        # bool 1   
        # num 1 byte 5/6 0-100 , 0-255
        # num 2 byte 0-32767, order float 
        # num 4 byte -32766- +32767 order float 
        #s7_dpt 
        #bit        1   = 1bit
        #byte=      5/6 = 8bit
        #wort =     9   = 16bit
        #doppelwort 14  = 32bit
        #string     16  
        
        if not self.init_webinterface():
            self._init_complete = False
            
        self.connect()
        self._lock = threading.Lock()

        if read_cyl:
            self._sh.scheduler.add('S7 read cycle', self._read, prio=5, cycle=self._cycle)
        

        
        return
    # ----------------------------------------------------------------------------------------------
    # Connect to PLC
    # ----------------------------------------------------------------------------------------------
    def connect(self):
        if self.client_read.get_connected() == False:
            try:
                #self.client_read.disconnect()
                #self.client_read.destroy()
                self.client_read.connect(self._host, self._rack, self._slot, self._port)
                
                
                self.logger.debug("S7: CPU Status: {0}".format(self.client_read.get_cpu_state()))
            except Snap7Exception:
                self.logger.error("S7: Could not connect to PLC with IP: {}".format(self._host))
                
                
        if self.client_write.get_connected() == False:
            try:
                #self.client_read.disconnect()
                #self.client_read.destroy()
                self.client_write.connect(self._host, self._rack, self._slot, self._port)
                
                
                self.logger.debug("S7: CPU Status: {0}".format(self.client_write.get_cpu_state()))
            except Snap7Exception:
                self.logger.error("S7: Could not connect to PLC with IP: {}".format(self._host))

    # ----------------------------------------------------------------------------------------------
    # Daten schreiben, über SHNG bei item_Change
    # schreibt 1 item
    # ----------------------------------------------------------------------------------------------
    def groupwrite(self, ga, item, dpt):
        payload = item()        
        s7area, dbnum, byte, bit = self.split_ga(ga)
        self.logger.debug("S7: WRITE payload {0},from area: {1} and adress{2}, dpt:{3} from itemid{3}".format(payload,s7area, [dbnum, byte, bit], dpt, item.id()))
        #self._lock.acquire()
        self.start_time_write  = time.time()
        try:
            if dpt == '1':              #Schreibe Bool
                #read_area(area, dbnumber, start, size)
                size = 1
                self.write_data(s7area, dbnum, byte, bit, size, payload )
            elif dpt == '5':            #Schreibe Dezimalzahl
                #set_int(_bytearray, byte_index, _int)
                size = 2
                if payload < 32768 and payload > -32767:
                    self.write_data(s7area, dbnum, byte, bit, size, payload)
                else:
                    self.logger.error("S7: Could not write {0}, Payload bigger than 2 Bytes! (-32767<payload<32768)".format(payload))
                    
            elif dpt == '6':            #Schreibe Gleitzahl
                #set_real(_bytearray, byte_index, real)
                size = 4
                self.write_data(s7area, dbnum, byte, bit, size, payload )
            elif dpt == '16':            #Schreibe Gleitzahl
                #set_real(_bytearray, byte_index, real)
                size = 32
                self.write_data(s7area, dbnum, byte, bit, size, payload )
            
            self.logger.debug("S7: schreibe den Wert {0} an area {2} {1}".format(payload, [dbnum, byte, bit] ,s7area) )    
                
        except Snap7Exception as e:
            self.logger.error("S7: Error writing {0} to {1} with function {2} {3}".format(payload,[dbnum, byte, bit],s7area, e))
            if not self.client_write.get_connected():
                self.logger.error("S7: Not connected! -> connecting".format())
                self.connect()
        finally:
            #self._lock.release()
            self.stop_time_write = time.time()            
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, zyklisch
    # liest alle s7 items
    # ----------------------------------------------------------------------------------------------     
    def _read(self):
        #for ga in self._init_ga:
            #val = 0 			                #Item-Value
        #    src = ga			                #Source-Item      (Quell-Adresse)
        #    dst = ga 			                #Destination-Item (Ziel-Adresse)
 
            
        #self._lock.acquire()
        self.start_time_read  = time.time()      
        try:
            #for item in self.gal[dst]['items']:
            for ga in self.gal:             #self.gal[ga] = {'dpt': dpt, 'item': item}
                
                dpt = self.gal[ga]['dpt']
                item = self.gal[ga]['item']
                s7area, dbnum, byte, bit = self.split_ga(ga)
                dpt = item.conf['s7_dpt']
                #payload = item()
                
                #self.logger.debug("S7: Read Value from Dpt: {0},area {1},ga  {2} ".format(dpt, s7area, [dbnum, byte, bit]))
               
                if dpt == '1':              #Lese Bool
                    size = 1
                    val = self.read_data(s7area, dbnum, byte, bit, size)
                    
                elif dpt == '5':            #Lese Dezimalzahl
                    
                    size = 2
                    val = self.read_data(s7area, dbnum, byte, bit, size)
                    
                elif dpt == '6':            #Lese Gleitzahl
                    size = 4
                    val = self.read_data(s7area, dbnum, byte, bit, size)
                    
                elif dpt == '16':           #Lese String
                    size = 32
                    val = self.read_data(s7area, dbnum, byte, bit, size)
                item(val, 'S7',[dbnum, byte, bit])
                self.logger.debug("S7: Read {0} from {1}-{2}, Set value to Item {3} ".format(val,s7area, [dbnum, byte, bit], item() ))
                  
        except Exception as e:
            self.logger.warning("S7: Could not read {0} from {1} because {2}".format(item,[dbnum, byte, bit],e))
            if not self.client_read.get_connected():
                self.logger.error("S7: Not connected! -> connecting".format())
                self.connect()
        finally:
            #self._lock.release()
            self.stop_time_read = time.time()
            
    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        self.client_read.disconnect()
        self.client_read.destroy()
        self.client_write.disconnect()
        self.client_write.destroy()
        self._lock.release()
        
    def parse_item(self, item):
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
        if self.has_iattr(item.conf, 's7_dtp'):
            self.logger.warning("S7: Ignoring {0}: please change s7_dtp to s7_dpt.".format(item))
            return None
        elif self.has_iattr(item.conf, 's7_dpt'):
            dpt = item.conf['s7_dpt']
            if dpt not in ['1','5','6','16']:
                self.logger.warning("S7: This is not a valid dpt.{0} {1}.".format(item, dpt))
                return None

            if self.has_iattr(item.conf, 's7_read'):
                ga = item.conf['s7_read']
                if '|' not in ga:
                    self.logger.info("S7: No Function (I,Q, M, C, T) for {} given, using default DB ".format(item))
                self.logger.debug("S7: {0} listen on and init with {1}".format(item, ga))
                #self._init_ga.append(ga)
                
                if not ga in self.gal:
                    self.gal[ga] = {'dpt': dpt, 'item': item}
                return self.update_item_send

            if self.has_iattr(item.conf, 's7_send'):
                #ga = item.conf['s7_send']
                return self.update_item_send

    def update_item_send(self, item, caller=None, source=None, dest=None):
        if caller != 'S7':
            if self.has_iattr(item.conf, 's7_send'):
                if self.client_write.get_connected:
                    #for ga in item.conf['s7_send']:    
                    self.groupwrite(item.conf['s7_send'], item, item.conf['s7_dpt'])

    #1 byte  to 0-100%
    def byte_to_dpt5(_val):
      return round(_val/327.67)
    #gloat to int
    def byte_to_dpt7(_val):
      return int(_val)
    # ----------------------------------------------------------------------------------------------
    # splitetet die S7 byts/bits
    # 
    # ----------------------------------------------------------------------------------------------   
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
    # ----------------------------------------------------------------------------------------------
    # liest daten, verändert diese und 
    # schreibt 1 item
    # ---------------------------------------------------------------------------------------------- 
    def write_data(self, area, db, byte, bit, size, payload):
        #read_area(area, dbnumber, start, size)
        #self._lock.acquire()
        ret_val = self.client_write.read_area(area, db, byte, size)
        if size == 1:
            snap7.util.set_bool(ret_val, 0, bit, payload)
        elif size == 2:
        #set_int(_bytearray, byte_index, _int)
            snap7.util.set_int(ret_val, 0, payload)
        elif size == 4:
        #set_real(_bytearray, byte_index, real)
            snap7.util.set_real(ret_val, 0, payload)
        elif size == 32:
            #_bytearray, byte_index, value, max_size)
            self.logger.debug("S7: Write Funktion read {0}".format([ret_val,payload, size]))
            snap7.util.set_string(ret_val, 1, str(payload), size)
        #self.logger.debug("S7: Write_data Funktion  {0} on Area {1} with Adress {2}\{3}\{4} ans size {5}".format(payload,area, db, byte, bit, size ))
        #self._lock.release()
        return self.client_write.write_area(area,db, byte, ret_val)
    # ----------------------------------------------------------------------------------------------
    # 
    # liest 1 item
    # ---------------------------------------------------------------------------------------------- 
    def read_data(self, area, db, byte, bit, size):
        #self._lock.acquire()
        ret_val = self.client_read.read_area(area, db, byte, size)
        #self.logger.debug("S7: Write Funktion read {0}".format(ret_val))
        
        #set_bool(_bytearray, byte_index, bool_index, value
        if size == 1:
            payload = snap7.util.get_bool(ret_val, 0, bit)
        elif size == 2:
        #set_int(_bytearray, byte_index, _int)
            payload = snap7.util.get_int(ret_val, 0)
        elif size == 4:
        
        #set_real(_bytearray, byte_index, real)
            payload = snap7.util.get_real(ret_val, 0)
        elif size == 32:
            payload = str(snap7.util.get_string(ret_val, 0, size))
        #self.logger.debug("S7: Read_data Funktion  {0} on Area {1} with Adress {2}\{3}\{4} ans size {5}".format(payload,area, db, byte, bit, size ))
        #self._lock.release() 
        return payload
        
    # ----------------------------------------------------------------------------------------------
    # Methoden, welche über webif aufgerufen werden
    # 
    # ---------------------------------------------------------------------------------------------- 
    def get_connection_info(self):
        info = {}
        info['ip'] = self._host
        info['port'] = self._port
        info['rack'] = self._rack
        info['slot'] = self._slot
        info['cycle'] = self._cycle
        if self.client_write.get_connected():
            try:
                info['status'] =  self.client_read.get_cpu_state()
            except Exception as e:
                info['status'] = "Not Connected"

            
        try:
            info['info'] = self.client_read.get_cpu_info()
        except Exception as e:
            self.logger.debug("S7: No CPU info, while {}".format(e))
            info['info'] = ''
        return info
        
    def set_cpu_status(self, status):
        self.logger.debug("S7: Plugin set status {}".format(status))
        if status == "stop":
            #self._sh.scheduler.add('S7 read cycle', self._read, prio=5, cycle=self._cycle)
            self.client_write.plc_stop()
        elif status =="coldstart":
            #self._sh.scheduler.add('S7 read cycle', self._read, prio=5, cycle=self._cycle)
            self.client_write.plc_cold_start()        
        elif status =="hotstart":
            #self._sh.scheduler.add('S7 read cycle', self._read, prio=5, cycle=self._cycle)
            self.client_write.plc_hot_start()
    
    def send_cpu_cmd(self, cmd=None):
        if cmd == 'list_blocks':
            return self.client_read.list_blocks()
    
    def init_webinterface(self):
        """"
        Initialize the web interface for this plugin

        This method is only needed if the plugin is implementing a web interface
        """
        try:
            self.mod_http = Modules.get_instance().get_module(
                'http')  # try/except to handle running in a core version that does not support modules
        except:
            self.mod_http = None
        if self.mod_http == None:
            self.logger.error("Plugin '{}': Not initializing the web interface".format(self.get_shortname()))
            return False

        # set application configuration for cherrypy
        webif_dir = self.path_join(self.get_plugin_dir(), 'webif')
        config = {
            '/': {
                'tools.staticdir.root': webif_dir,
            },
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': 'static'
            }
        }
        
        self.logger.debug("Plugin '{0}': {1}, {2}, {3}, {4}, {5}".format(self.get_shortname(), webif_dir, self.get_shortname(),config,  self.get_classname(), self.get_instance_name()))
        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True


# ------------------------------------------
#    Webinterface of the plugin
# ------------------------------------------

import cherrypy
from jinja2 import Environment, FileSystemLoader

class WebInterface(SmartPluginWebIf):


    def __init__(self, webif_dir, plugin):
        """
        Initialization of instance of class WebInterface

        :param webif_dir: directory where the webinterface of the plugin resides
        :param plugin: instance of the plugin
        :type webif_dir: str
        :type plugin: object
        """
        self.logger = logging.getLogger(__name__)
        self.webif_dir = webif_dir
        self.plugin = plugin
        self.tplenv = self.init_template_environment()
        self.logger.debug("Plugin : Init Webif")
        self.items = Items.get_instance()
        
    @cherrypy.expose
    def index(self, reload=None):
        """
        Build index.html for cherrypy
        Render the template and return the html file to be delivered to the browser
        :return: contents of the template after beeing rendered
        """
        plgitems = []
        for item in self.items.return_items():
            if ('s7_dpt' in item.conf):
                plgitems.append(item)
        read_cycle_time = round(self.plugin.stop_time_read - self.plugin.start_time_read, 2) 
        write_cycle_time = round(self.plugin.stop_time_write - self.plugin.start_time_write, 2) 
        self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), 
                            plugin_version=self.plugin.get_version(),
                            plugin_info=self.plugin.get_info(),
                            p=self.plugin,
                            webif_dir = self.webif_dir ,
                            read_cycle = read_cycle_time,
                            write_cycle = read_cycle_time,
                            connection = self.plugin.get_connection_info(),
                            items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
                            
    @cherrypy.expose
    def action(self, name=None):
        self.logger.debug("Plugin {0}: CherryPi Call action {1}".format(self.plugin, name))
        if name == 'stop':
            self.plugin.set_cpu_status("stop")
        elif name == 'warmstart':
            self.plugin.set_cpu_status("warmstart")
        elif name == 'coldstart':
            self.plugin.set_cpu_status("coldstart")


    ##cherrypy.engine.subscribe('start', open_page)
    #cherrypy.tree.mount(AjaxApp(), '/', config=config)
    #cherrypy.engine.start()
