#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################
#
#  Copyright 2018 Version-1    Manuel Holländer

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
#   VERSION - 1
#
####################################################################################
# 
import logging
import threading
import struct
import binascii
import re
import time

import miio
from miio.vacuum import Vacuum, VacuumException
from miio.vacuumcontainers import (VacuumStatus, ConsumableStatus, DNDStatus, CleaningDetails, CleaningSummary, Timer, )
from miio.discovery import Discovery

from lib.model.smartplugin import SmartPlugin

class Robvac(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="0.0.1"
    
    def __init__(self, smarthome,ip='127.0.0.1', token='', read_cyl=60):
        self._ip = str(ip)
        self._token = str(token)
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        
        self.messages = {}
        self.max_ret = 3
        self.count_ret = 0
        self.found = False
        self._lock = threading.Lock()
        self.retr_count_max = 3
        self.retr_count = 1
        self._connected = False

        if self._token == '':
            self.logger.error("Xiaomi_Robvac: No Key for Communication given, Plugin would not start!")
            pass
        else:
            self.logger.debug("Xiaomi_Robvac: Plugin Start!")
            if read_cyl:
                self._sh.scheduler.add('Xiaomi_Robvac read cycle', self._read, prio=5, cycle=int(read_cyl))
    # ----------------------------------------------------------------------------------------------
    # Verbinden zum Roboter
    # ----------------------------------------------------------------------------------------------
    def _connect(self):        
            if self._connected == False:
                for i in range(self.retr_count_max-self.retr_count):
                    try:
                        self.vakuum = miio.Vacuum(self._ip,self._token, 0, 0)
                        #robots = self.vakuum.find()
                        
                        #self.logger.debug("Xiaomi_Robvac: Found some Robots!{}".format(robots))
                        self.retr_count = 1
                        self._connected = True
                        return True
                        break
                    except Exception as e:
                        self.logger.error("Xiaomi_Robvac: Error {0}, Cycle {1} ".format(e,self.retr_count))
                        self.retr_count += 1
                        self._connected = False
                    finally:
                        return False
            
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
            data['clean_count'] =           clean_history.count
            data['clean_total_area'] =      clean_history.total_area
            data['clean_tital_duration'] =  clean_history.total_duration
            data['clean_ids'] =             clean_history.ids.sort(reverse = True)
            
            #->2018-12-26  11:10:37 DEBUG    plugins.xiaomi_vac Xiaomi_Robvac: Letze Reinigung Details<CleaningDetails: 2018-11-01 16:18:27 (duration: 0:00:05, done: 
                        #historische reinigung
            
            #_>2018-12-26  11:10:37 DEBUG    plugins.xiaomi_vac Xiaomi_Robvac: Histroische daten Reinigung <CleaningSummary: 23 times, total time: 14:01:42, total area: 556.2675, ids: [1545742801, 1545483493, 1545397202, 1544349386, 1544187601, 1543928402, 1543585780, 1543323601, 1542978001, 1542732823, 1542718801, 1542373202, 1542114000, 1541768401, 1541509200, 1541166079, 1541163602, 1541095176, 1541090077, 1541085507]>
            
            #letzte reinigung
            #funktioniert nur mit übergebener id
            data['clean_details_last'] = self.vakuum.clean_details(data['clean_ids'][0])
            data['clean_details_last1'] = self.vakuum.clean_details(data['clean_ids'][1])
            data['clean_details_last2'] = self.vakuum.clean_details(data['clean_ids'][2])
            

            self.logger.debug("Xiaomi_Robvac: Historische daten Reinigung {0}".format(clean_history))
            
            carpet_mode = self.vakuum.carpet_mode()
            data['carpetmode_high'] =       carpet_mode.current_high
            data['carpetmodes_integral'] =  carpet_mode.current_integral
            data['carpetmode_low'] =        carpet_mode.current_low
            data['carpetmode_enabled'] =    carpet_mode.enabled
            data['carpetmode_stall_time'] = carpet_mode.stall_time

            #status
            data['serial'] =    self.vakuum.serial_number()
            data['vol'] =       self.vakuum.sound_volume()
            data['dnd_status'] = self.vakuum.dnd_status().enabled
            data['dnd_start'] = self.vakuum.dnd_status().start
            data['dnd_end'] =   self.vakuum.dnd_status().end
            self.logger.debug("Xiaomi_Robvac: Lese fanspeed {0}, vol {1}, dnd {2}".format(data['fanspeed'], data['vol'], dnd))
            data['fanspeed'] =  self.vakuum.fan_speed
            data['batt'] =      self.vakuum.status().battery
            data['area'] =      self.vakuum.status().clean_area
            data['cleantime'] = self.vakuum.status().clean_time.seconds
            data['aktiv'] =     self.vakuum.status().is_on #reinigt?
            data['zone_cleaning'] = self.vakuum.status().in_zone_cleaning #reinigt?
            data['error'] =     self.vakuum.status().error_code
            data['pause'] =     self.vakuum.status().is_paused #reinigt? 
            data['status'] =    self.vakuum.status().state #status charging
            data['timer'] =     self.vakuum.timer()
            data['timezone'] =  self.vakuum.timezone()
            #->2018-12-26  11:10:37 DEBUG    plugins.xiaomi_vac Xiaomi_Robvac: Lese batt 100 area0.0 time 0:00:15 status False stateCharging
            self.logger.debug("Xiaomi_Robvac: Lese batt {0} area{1} time {2} status {3} state{4}".format(data['batt'], data['area'], data['cleantime'], data['status'], data['status']))
            #buerste
            #consumable_status()
            data['sensor_dirty'] =      self.vakuum.consumable_status().sensor_dirty.seconds
            data['sensor_dirty_left'] = self.vakuum.consumable_status().sensor_dirty_left.seconds
            data['side_brush'] =        self.vakuum.consumable_status().side_brush
            data['side_brush_left'] =   self.vakuum.consumable_status().side_brush_left
            data['main_brush'] =        self.vakuum.consumable_status().main_brush
            data['main_brush_left'] =   self.vakuum.consumable_status().main_brush_left
            data['filter'] =            self.vakuum.consumable_status().filter
            data['filter_left'] =       self.vakuum.consumable_status().filter_left
            self.logger.debug("Xiaomi_Robvac: buerste seite {0}/{1} Buerste Haupt {2}/{3} filter{4}/{5}".format(data['side_brush'], 
                                                                                                                data['side_brush_left'], 
                                                                                                                data['main_brush'], 
                                                                                                                data['main_brush_left'], 
                                                                                                                data['filter'], 
                                                                                                                data['filter_left']))
            self.logger.debug("Xiaomi_Robvac:{}".format(data))
        except Exception as e:
                self.logger.error("Xiaomi_Robvac: Error {}".format(e))
                self._connected = False    
        

        for x in data:
            if x in self.messages:
                self.logger.debug("Xiaomi_Robvac: Update item {1} mit key {0} = {2}".format(x, self.messages[x], data[x]))
                item = self.messages[x]
                item(data[x], 'Xiaomi Robovac')

    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit robvac ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Robvac':
            #if 'robvac' in item.conf:
            #    message = item.conf['robvac']
            if self.has_iattr(item.conf, 'robvac'):
                message = self.get_iattr_value(item.conf, 'robvac')
                self.logger.debug("Xiaomi_Robvac: Tu dies und das !{0} , weil item {1} geändert wurde".format(message, item))
                if message == 'fan_speed':
                    self.vakuum.set_fan_speed(item())
                    self.logger.debug("Xiaomi_Robvac: Hab {0} geaendert wurde".format(self.vakuum.fan_speed())) 
                elif message == 'vol':
                    if item() > 100:
                        vol = 100
                    else:
                        vol = item()
                    self.vakuum.set_sound_volume(vol)
                elif message == 'start':
                    self.vakuum.start()
                elif message == 'stop':
                    self.vakuum.home()
                elif message == "pause":
                    self.vakuum.pause()
                elif message == "spot":
                    self.vakuum.spot()
                elif message == "find":
                    self.vakuum.find()
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

