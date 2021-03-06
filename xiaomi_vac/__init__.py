#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################
#
#  Copyright 2018 Version-1    Manuel Holländer
#  Copyright 2019 Version-2    Manuel Holländer
####################################################################################
#
#  This Plugin is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  smarthomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHome.py. If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################
#
#   VERSION - 2
#
####################################################################################
# 
import logging
import threading
import struct
import binascii
import re
import time
from datetime import datetime, timedelta

import miio
from miio.vacuum import Vacuum, VacuumException
from miio.vacuumcontainers import (VacuumStatus, ConsumableStatus, DNDStatus, CleaningDetails, CleaningSummary, Timer)
from miio.discovery import Discovery

from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class Robvac(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"
    
    def __init__(self, smarthome,ip='127.0.0.1', token='', read_cycle=20):
        self._ip = str(ip)
        self._token = str(token)
        self._cycle = int(read_cycle)
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        
        self.messages = {}
        self.found = False
        self._lock = threading.Lock()
        self.retry_count_max = 3
        self.retry_count = 1
        self._connected = False
        self._data = {}
        if not self.init_webinterface():
            self._init_complete = False
            
        if self._token == '':
            self.logger.error("Xiaomi_Robvac: No Key for Communication given, Plugin would not start!")
            pass
        else:
            self.logger.debug("Xiaomi_Robvac: Plugin Start!")
            if self._cycle > 10:
                self._sh.scheduler.add('Xiaomi_Robvac Read cycle', self._read, prio=5, cycle=self._cycle)
            else:
                self.logger.warning("Xiaomi_Robvac: Read Cycle is to fast! < 10s, not starting!")
    # ----------------------------------------------------------------------------------------------
    # Verbinden zum Roboter
    # ----------------------------------------------------------------------------------------------
    def _connect(self):        
            if self._connected == False:
                for i in range(0,self.retry_count_max-self.retry_count):
                    try:
                        self.vakuum = miio.Vacuum(self._ip,self._token, 0, 0)
                        self.retry_count = 1
                        self._connected = True
                        return True
                    except Exception as e:
                        self.logger.error("Xiaomi_Robvac: Error {0}, Cycle {1} ".format(e,self.retry_count))
                        self.retry_count = self.retry_count+1
                        self._connected = False
                        return False
                    #finally:
                        
            
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, über SHNG bei item_Change
    # ----------------------------------------------------------------------------------------------
    def groupread(self, ga, dpt):
        pass
        
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, zyklisch
    # ----------------------------------------------------------------------------------------------     

    
    def _read(self):
        data = {}
        #config
        self._connect()

        try:
            clean_history = self.vakuum.clean_history()
            self._data['clean_total_count'] =     int(clean_history.count)
            self._data['clean_total_area'] =      round(clean_history.total_area,2)
            self._data['clean_total_duration'] =  clean_history.total_duration.total_seconds() // 3600
            self._data['clean_ids'] =             clean_history.ids
            self.logger.debug("Xiaomi_Robvac: Reingungsstatistik Anzahl {0}, Fläche {1}², Dauer {2}, clean ids {3}".format(
                                                                                                    self._data['clean_total_count'], 
                                                                                                    self._data['clean_total_area'], 
                                                                                                    self._data['clean_total_duration'], 
                                                                                                    self._data['clean_ids']))

            #letzte reinigung
            #funktioniert nur mit übergebener id
            if self._data['clean_ids'] != None:
                #self._data['clean_ids'] = self._data['clean_ids'].sort(reverse=True)
                self._data['clean_details_last0'] = self.vakuum.clean_details(self._data['clean_ids'][0],return_list=True)
                self._data['last0_area'] =          round(self._data['clean_details_last0'][0].area,2)
                self._data['last0_complete'] =      self._data['clean_details_last0'][0].complete
                self._data['last0_duration'] =      round(self._data['clean_details_last0'][0].duration.total_seconds()/ 3600,2)
                self._data['last0_start_date'] =    self._data['clean_details_last0'][0].start.strftime("%d.%m.%Y")
                self._data['last0_start_time'] =    self._data['clean_details_last0'][0].start.strftime("%H:%M")                 
                self._data['last0_end_date'] =      self._data['clean_details_last0'][0].start.strftime("%d.%m.%Y")
                self._data['last0_end_time'] =      (self._data['clean_details_last0'][0].start+self._data['clean_details_last0'][0].duration).strftime("%H:%M")
                
                self._data['clean_details_last1'] = self.vakuum.clean_details(self._data['clean_ids'][1],return_list=True)
                self._data['last1_area'] =          round(self._data['clean_details_last1'][0].area,2)
                self._data['last1_complete'] =      self._data['clean_details_last1'][0].complete
                self._data['last1_duration'] =      round(self._data['clean_details_last1'][0].duration.total_seconds()/ 3600,2)
                self._data['last1_start_date'] =    self._data['clean_details_last1'][0].start.strftime("%d.%m.%Y")
                self._data['last1_start_time'] =    self._data['clean_details_last1'][0].start.strftime("%H:%M")                 
                self._data['last1_end_date'] =      self._data['clean_details_last1'][0].start.strftime("%d.%m.%Y")
                self._data['last1_end_time'] =      (self._data['clean_details_last1'][0].start+self._data['clean_details_last1'][0].duration).strftime("%H:%M")
                
                self._data['clean_details_last2'] = self.vakuum.clean_details(self._data['clean_ids'][2],return_list=True)
                self._data['last2_area'] =          round(self._data['clean_details_last2'][0].area,2)
                self._data['last2_complete'] =      self._data['clean_details_last2'][0].complete
                self._data['last2_duration'] =      round(self._data['clean_details_last2'][0].duration.total_seconds()/ 3600,2)
                self._data['last2_start_date'] =    self._data['clean_details_last2'][0].start.strftime("%d.%m.%Y")
                self._data['last2_start_time'] =    self._data['clean_details_last2'][0].start.strftime("%H:%M")   
                self._data['last2_end_date'] =      self._data['clean_details_last2'][0].start.strftime("%d.%m.%Y")
                self._data['last2_end_time'] =      (self._data['clean_details_last2'][0].start+self._data['clean_details_last2'][0].duration).strftime("%H:%M")
                
                self._data['clean_details_last3'] = self.vakuum.clean_details(self._data['clean_ids'][3],return_list=True)
                self._data['last3_area'] =          round(self._data['clean_details_last3'][0].area,2)
                self._data['last3_complete'] =      self._data['clean_details_last3'][0].complete
                self._data['last3_duration'] =      round(self._data['clean_details_last3'][0].duration.total_seconds()/ 3600,2)
                self._data['last3_start_date'] =    self._data['clean_details_last3'][0].start.strftime("%d.%m.%Y")
                self._data['last3_start_time'] =    self._data['clean_details_last3'][0].start.strftime("%H:%M")   
                self._data['last3_end_date'] =      self._data['clean_details_last3'][0].start.strftime("%d.%m.%Y")
                self._data['last3_end_time'] =      (self._data['clean_details_last3'][0].start+self._data['clean_details_last3'][0].duration).strftime("%H:%M")
                
                self.logger.debug("Xiaomi_Robvac: Historische id1 {}, id2{}, id3 {}".format(self._data['clean_details_last0'],
                                                                                            self._data['clean_details_last1'],
                                                                                            self._data['clean_details_last2']))
                                                                                            
                self.logger.debug("Xiaomi_Robvac: Clean Run complete id1 {}, id2{}, id3 {}".format(self._data['last1_complete'],
                                                                                            self._data['last2_complete'],
                                                                                            self._data['last3_complete'],))
            carpet_mode = self.vakuum.carpet_mode()
            self._data['carpetmode_high'] =       carpet_mode.current_high
            self._data['carpetmode_integral'] =  carpet_mode.current_integral
            self._data['carpetmode_low'] =        carpet_mode.current_low
            self._data['carpetmode_enabled'] =    carpet_mode.enabled
            self._data['carpetmode_stall_time'] = carpet_mode.stall_time
            self.logger.debug("Xiaomi_Robvac: Carpet Mode high: {}, integral: {}, low: {}, enabled: {}, , stall_time: {}".format(self._data['carpetmode_high'],
                                                                                                    self._data['carpetmode_integral'],
                                                                                                    self._data['carpetmode_low'],
                                                                                                    self._data['carpetmode_enabled'],
                                                                                                    self._data['carpetmode_stall_time']))
           
            #status
            self._data['serial'] =    self.vakuum.serial_number()
            self._data['vol'] =       self.vakuum.sound_volume()
            self._data['dnd_status'] = self.vakuum.dnd_status().enabled
            self._data['dnd_start'] = self.vakuum.dnd_status().start
            self._data['dnd_end'] =   self.vakuum.dnd_status().end
            self.logger.debug("Xiaomi_Robvac: Serial{}, vol {}, dnd status {}, dnd start {},dnd end {},".format(self._data['serial'],
                                                                                                    self._data['vol'],
                                                                                                    self._data['dnd_status'],
                                                                                                    self._data['dnd_start'],
                                                                                                    self._data['dnd_end']))
            
            self._data['device_group'] = self.vakuum.get_device_group()
            self._data['segment_status'] = self.vakuum.get_segment_status()
            self._data['fanspeed'] =  self.vakuum.status().fanspeed
            self._data['batt'] =      self.vakuum.status().battery
            self._data['area'] =      round(self.vakuum.status().clean_area,2)
            self._data['cleantime'] = self.vakuum.status().total_seconds() // 3600
            self._data['aktiv'] =     self.vakuum.status().is_on #reinigt?
            self._data['zone_cleaning'] = self.vakuum.status().in_zone_cleaning #reinigt?
            self._data['is_error'] = self.vakuum.status().got_error 
            self.logger.debug("Xiaomi_Robvac: segment_status, fanspeed {},batt {}, area {}, cleantime {}, aktiv {} zonen_reinigung {} , device group{}".format(self._data['segment_status'], self._data['fanspeed'], 
                                                                                                    self._data['batt'], 
                                                                                                    self._data['area'], 
                                                                                                    self._data['cleantime'], 
                                                                                                    self._data['aktiv'], 
                                                                                                    self._data['zone_cleaning'], 
                                                                                                    self._data['device_group']))
            self._data['error'] =     self.vakuum.status().error_code
            self._data['pause'] =     self.vakuum.status().is_paused #reinigt? 
            self._data['status'] =    self.vakuum.status().state #status charging
            self._data['timer'] =     self.vakuum.timer()#[self.vakuum.timer()[0]['id'], self.vakuum.timer()[0]['action'], self.vakuum.timer()[0]['enabled'], self.vakuum.timer()[0]['ts']] 
            self._data['timezone'] =  self.vakuum.timezone()
           
            #bekannet States: Charging, Pause, Charging Disconnected 
            if self._data['status'] == 'Charging':
                self._data['charging'] = True
            else:
                self._data['charging'] = False

            #->2018-12-26  11:10:37 DEBUG    plugins.xiaomi_vac Xiaomi_Robvac: Lese batt 100 area0.0 time 0:00:15 status False stateCharging
            self.logger.debug("Xiaomi_Robvac: error {}, pause {}, status{} , timer {}, timezone{}".format(   self._data['error'], 
                                                                                                       self._data['pause'], 
                                                                                                       self._data['status'], 
                                                                                                       self._data['timer'], 
                                                                                                       self._data['timezone']))
            #buerste
            #consumable_status()
            self._data['sensor_dirty'] =      self.vakuum.consumable_status().sensor_dirty.total_seconds() // 3600
            self._data['sensor_dirty_left'] = self.vakuum.consumable_status().sensor_dirty_left.total_seconds()// 3600
            self._data['side_brush'] =        self.vakuum.consumable_status().side_brush.total_seconds() // 3600
            self._data['side_brush_left'] =   self.vakuum.consumable_status().side_brush_left.total_seconds() // 3600
            self._data['main_brush'] =        self.vakuum.consumable_status().main_brush.total_seconds() // 3600
            self._data['main_brush_left'] =   self.vakuum.consumable_status().main_brush_left.total_seconds() // 3600
            self._data['filter'] =            self.vakuum.consumable_status().filter.total_seconds() // 3600
            self._data['filter_left'] =       self.vakuum.consumable_status().filter_left.total_seconds() // 3600
            self.logger.debug("Xiaomi_Robvac: buerste seite {0}/{1} Buerste Haupt {2}/{3} filter{4}/{5}".format(self._data['side_brush'], 
                                                                                                                self._data['side_brush_left'], 
                                                                                                                self._data['main_brush'], 
                                                                                                                self._data['main_brush_left'], 
                                                                                                                self._data['filter'], 
                                                                                                                self._data['filter_left']))
            self.logger.debug("Xiaomi_Robvac:{}".format(self._data))
        except Exception as e:
                self.logger.error("Xiaomi_Robvac: Error {}".format(e))
                self._connected = False
        

        for x in self._data:
            if x in self.messages:
                self.logger.debug("Xiaomi_Robvac: Update item {1} mit key {0} = Wert {2}".format(x, self.messages[x], self._data[x]))
                item = self.messages[x]
                item(self._data[x], 'Xiaomi Robovac')
                

    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit robvac ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Robvac':
            #if 'robvac' in item.conf:
            #    message = item.conf['robvac']
            if self.has_iattr(item.conf, 'robvac'):
                #bei boolischem item Item zurücksetzen, damit enforce_updates nicht nötig!
               
                message = self.get_iattr_value(item.conf, 'robvac')
                self.logger.debug("Xiaomi_Robvac: Tu dies und das ! Keyword {0} , weil item {1} geändert wurde   ".format(message, item))
                
                if message == 'fanspeed':
                    self.vakuum.set_fan_speed(item())
                    self.logger.debug("Xiaomi_Robvac: {0} geaendert wurde ".format(self.vakuum.fan_speed())) 
                elif message == 'vol':
                    if item() > 100:
                        vol = 100
                    else:
                        vol = item()
                    self.vakuum.set_sound_volume(vol)
                elif message == 'set_start':
                    if item() == True:
                        item(False, 'Robvac')
                    self.vakuum.start()
                elif message == 'set_stop':
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.pause()
                elif message == "set_home":
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.home()
                elif message == "set_pause":
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.pause()
                elif message == "set_spot":
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.spot()
                elif message == "set_find":
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.find()
                elif message == "reset_filtertimer":
                    if item() == True:
                       item(False, 'Robvac')                    
                    self.vakuum.reset_consumable()
                elif message == "disable_dnd":
                    if item() == True:
                       item(False, 'Robvac')
                    self.vakuum.disable_dnd()
                    
                elif message == "set_dnd":
                
                    if item() == True:
                       item(False, 'Robvac')
                    #start_hr, start_min, end_hr, end_min
                    self.vakuum.set_dnd(item()[0], item()[1],item()[2], item()[3])
                elif message == "clean_zone":
                #Clean zones. :param List zones: List of zones to clean: [[x1,y1,x2,y2, iterations],[x1,y1,x2,y2, iterations]]
                    self.vakuum.zoned_clean(item())
                elif message == "segment_clean":
                    self.vakuum.segment_clean(item())
                elif message == "go_to":    
                    self.vakuum.goto(item()[0], item()[1])
                elif message == "create_nogo_zones":
                    self.vakuum.create_nogo_zone(item()[0], item()[1])
                    pass
                    
    def run(self):
        self.alive = True
        self.logger.debug("Xiaomi_Robvac: Found items{}".format(self.messages))
        
    def stop(self):
        self.alive = False
        
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'robvac'):
            message = self.get_iattr_value(item.conf, 'robvac')
            self.logger.debug("Xiaomi_Robvac: {0} keyword {1}".format(item, message))

            if not message in self.messages:
                self.messages[message] = item
                
            return self.update_item

    def update_item_read(self, item, caller=None, source=None, dest=None):
        if self.has_iattr(item.conf, 'robvac'):
            for message in item.get_iattr_value(item.conf, 'robvac'):
            #for message in item.conf['robvac']:  # send status update
                self.logger.debug("Xiaomi_Robvac: update_item_read {0}".format(message))
# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------   

    def get_connection_info(self):
        info = {}
        info['ip'] = self._ip
        info['token'] = self._token
        info['cycle'] = self._cycle
        info['connected'] = self._connected
        return info
        
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
            if ('robvac' in item.conf):
                plgitems.append(item)
        self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), 
                            plugin_version=self.plugin.get_version(),
                            plugin_info=self.plugin.get_info(),
                            p=self.plugin,
                            connection = self.plugin.get_connection_info(),
                            webif_dir = self.webif_dir ,
                            items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
                            
