#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#########################################################################
# Copyright 2018 Manuel Holländer; Version 1.0
# based on the idea from baba from baba (baba@baba.tk) v1.5 Ip-Symcom

#########################################################################
#  This file is part of SmartHomeNG.
#  https://github.com/smarthomeNG/smarthome
#  http://knx-user-forum.de/
#
#  SmartHomeNG is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  SmartHomeNG is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with SmartHomeNG. If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import time
import re
import threading
import logging
import json

from lib.model.smartplugin import SmartPlugin
# importing the requests library
import requests

class RadioInet(SmartPlugin):
    """
    Main class of the Modbus TCP-Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """
    ALLOW_MULTIINSTANCE = True
    PLUGIN_VERSION="1.0.0"
    
    # Initialize connection
    def __init__(self, sh, device='', cycle='', item_subtree=''):
        """
        Initalizes the plugin. The parameters described for this method are pulled from the entry in plugin.yaml.

        :param sh:                 The instance of the smarthome object, save it for later references
        :param ip:                 hostip
        :param cycle:              number of seconds between updates
        """
        
        self.logger = logging.getLogger(__name__)
        
        #self.device = self.get_parameter_value('device')
        self.device = device
        if self.device  == '':
            self.logger.error("Radio Inet: No Device Ip specified, plugin is not starting")
        
        self.port = 4244
        #self.cycle = int(self.get_parameter_value('cycle'))
        self.cycle = int(float(cycle))
        if self.cycle =='':
            self.logger.info("Radio Inet: No Cycle specified, default 10s is used")
            self.cycle = 10
        
        #self.item_subtree = str(self.get_parameter_value('item_subtree'))
        self.item_subtree = str(item_subtree)
        if self.item_subtree == '':
            self.logger.warning("RadioInet: item_subtree is not configured, searching complete item-tree instead. Please configure item_subtree to reduce processing overhead" )   
        
        self._sh = sh

        #Listen
        self._itemlist = []                 #puffert die benutzen Radio Items
        self._data = { #enthält die configdaten
            'ah':'08', #alarmzeitstunden 0-23
            'am':'00',           #alarmzeitminuten 0-59
            'bb':'100',         #backgroundlight 0-100
            'bl':'1',             #backlight 0-2
            'dm':'0',             #lcdmodus 0-2
            'ea':'0',             #alarm 0-1
            'hr':'18',           #stunden 0-23
            'mi':'45',           #minuten 0-59
            'ln':'de',                #sprache de,fr,en,pl
            'ms':'1',             #audiomodus 0-1
            'sm':'0',             #soundmodus 0-5
            'sp':'0',             #netzspannung 0-1
            'ss':'00',           #timerzeit 0-60
            'et':'00',            #kurzzeittimer
            'st':'00',            #kurzzeittimerzeit
            'es':'00',            #sleeptimer
            'sw':'0',             #schaltfunktion
            'tz':'+1',            #zeitdifferenz
            'zs':'0'              #setzeitzone
            }
        self._stations = {} #enthält die stationsangaben

        #Read first TIme all Configuration Settings
        self.getConfiguration()
    def connect(self):
        pass
    def disconnect(self):
        pass
    def run(self):
        self.alive = True
        self._sh.scheduler.add(__name__, self.readSettings, prio=5, cycle=self.cycle, offset= 1)
    def stop(self):
        self.alive = False
        
    def parse_item(self, item):
        """
        Default plugin parse_item method. Is called when the plugin is initialized.
        The plugin can, corresponding to its attribute keywords, decide what to do with
        the item in future, like adding it to an internal array for future reference

        :param item:  The item to process
        :return:      If the plugin needs to be informed of an items change you should return a call back function
                      like the function update_item down below. An example when this is needed is the knx plugin
                      where parse_item returns the update_item function when the attribute knx_send is found.
                      This means that when the items value is about to be updated, the call back function is called
                      with the item, caller, source and dest as arguments and in case of the knx plugin the value
                      can be sent to the knx with a knx write function within the knx plugin.

        """
        # check for smarthome.py attribute 'radio' in yaml
        if self.has_iattr(item.conf, 'radio'):
            radio_function = self.get_iattr_value(item.conf,'radio')
            self._itemlist.append([item, radio_function, item()]);
            self.logger.info("RadioInet: parse Radio_inet item: {0} , Function {1}, Value {2}".format(item, radio_function,item()))
            return self.update_item
        
    def parse_logic(self, logic):
        pass
        
    def update_item(self, item, caller=None, source=None, dest=None):
        """
        Write items values

        This function is called by the core when a value changed, 
        so the plugin can update it's peripherals

        :param item:   item to be updated towards the plugin
        :param caller: if given it represents the callers name
        :param source: if given it represents the source
        :param dest:   if given it represents the dest
        """
        if caller != 'RadioInet':
            #self.logger.info("RadioInet: Es hat sich ein Item{0} geändert, paramter ist in den Rahmenwerten, zu Radio senden".format(item))
            self.logger.info("RadioInet: Es hat sich ein Item{0} geändert, paramter ist in den Rahmenwerten, zu Radio senden")
            
            radio_function = self.get_iattr_value(item.conf,'radio')
            self._data[radio_function] = item()
            self.sendSettings(item,radio_function,item())
            #self.logger.info("RadioInet: Set {0} to {1}, with  Function-Key {2}".format(item, item(), radio_function))
            #self.readSettings()           

   
    def readSettings(self):
        '''
        :HTTP VERSION
        :Read Stations and Values
        :param function: read all data cyclie from RadioInet
        :returns: true/false
        '''
        self.getStations()
        self.getConfiguration()
        self.updateItems()
        
    def updateItems(self):
        #write readed data from the data/stations dict , to the specified items! 
        #
        '''
        :param itemname: path/name of the Item
        :param data: the data to set the item
        :param function: the data to set the item
        :returns: true/false
        '''
        #itemlist[item, radio_function, value]
        #daten/settings = [['ah','08','23'], #alarmzeitstunden 0-23

        self.logger.debug("ItemList {0}".format(self._itemlist))
        for data in self._data.keys():
            for items in self._itemlist:#loop the itemlist
                #self.logger.debug("Item from ItemList {0}".format(items))            
                if items[1] == data:
                    items[0](self._data.get(data), 'RadioInet')
                    self.logger.info("RadioInet: Set {0} to {1}, with Function-Key {2}".format(items[0], items[1], self._data.get(data)))
                
        for stations in self._stations.keys():
            for items in self._itemlist:
                #self.logger.debug("Item from ItemList {0}".format(items))            
                if items[1] == stations:
                    items[0](self._stations.get(stations), 'RadioInet')
                    self.logger.info("RadioInet: Set {0} to {1}, with Function-Key {2}".format(items[0], items[1], self._stations.get(stations)))
        #self.findStation()
        
    def sendSettings(self, itemname, function, value):
        """
        Write items values to the RadioInet

        This function is called by the core when a value changed, 
        so the plugin can update it's peripherals
        """
        
        
        ##station editieren =post
        ##einstellungen speichern = post
        ##station aufrufen = get
        
        if function in ['vp','vm','vo', 'mute'] or function[0]== 'p':
            if function == "vp":
                param = {'vp':'  +  '}
                itemname(value,'RadioInet')
            elif function =="vm":
                param = {'vm':'  -  '}
                itemname(value,'RadioInet')
            elif function == 'vo':
                param = {'vo':value,'cv':'Setzen'}
            elif function == 'mute':
                param = {'vo':'0','cv':'Setzen'}
            
            elif function[0] == 'p':
                param = {function:' Abspielen '}
                itemname(True,'RadioInet')
                
            
            self.makeRequest("http://"+self.device+"/de/index.cgi", 'get', param)
        elif function in ['off']:
            
            self.logger.info("RadioINet: Ausschalten")
            sendCommand('SET', 'RADIO_OFF','shNG')
           
        else:#konfiguration post
            #bb=100&bl=2&dm=0&ms=1&sm=0&ln=de&hr=17&mi=01&zs=0&tz=%2B1&ah=08&am=00&st=00&ss=00&sw=0&sp=0&save=Save

            param = {function:value,"save":"Save"}
            self.logger.info("RadioINet: Send Setting Parameter-String {0}".format(param))          

            response = requests.post(url = "http://"+self.device+"/de/general.cgi", data = param)
            self.logger.info("RadioINet:{}".format(response)) 
            
    def makeRequest(self,_url,_type, _param):
        if _type == 'get':
            if _param != '':
                response = requests.get(url = _url, params = _param)
            else:
                response = requests.get(url = _url)
        elif _type == 'post':
            response = requests.post(url = _url, data = _param)
        
        if response.status_code > 200:
            self.logger.debug("RadioINet: Fehler beim Senden des Befehls an das Radio{}".format(response.status_code))
            return False
        else:
            self.logger.info("RadioINet: Senden OK {}".format(response.status_code)) 
            self.logger.debug("RadioINet: {}".format(response.text)) 
            return response

    def getConfiguration(self):
        #get configuration
        try:
            self.logger.info("RadioInet: Configuration")
            response = self.makeRequest("http://"+self.device+"/de/general.shtml", 'get', '')
            found = re.findall(r".? name=\"(.*?)\".*s.*?value=\"(.*?)\".?", response.text)
            self.logger.info("RadioInet: alte Konfigurations Daten{0}".format(self._data))
            for match in found:
                
                self._data[match[0]] = match[1] # daten in dict updaten
                self.logger.debug("RadioInet: gelesene Konfigurations  Daten{0} -> {1}".format(match[0],match[1]))
                
            response = self.makeRequest("http://"+self.device+"/de/general.shtml", 'get', '')
            found = re.findall(r".? name=\"(.*?)\".*?value=\"(.*?)\"\s(.*?)\s*>", response.text)
            for match in found:
                if len(match) == 3 and match[2] == 'checked':
                    self._data[match[0]] = match[1] # daten in dict updaten
                    self.logger.debug("RadioInet: gelesene Konfigurations Daten{0}{1}".format(match[0],match[1]))
                    
            self.logger.info("RadioInet: upgedatete Konfigurations Daten{0}".format(self._data))
        except OSError:
            self.logger.error("RadioInet: Fehlerbei der Datenabfrage von {}".format(self.device))
    def getStations(self):
        try:
            response = self.makeRequest("http://"+self.device+"/de/index.shtml", 'get', '')
            found = re.findall(r".? name=\"(.*?)\".*s.*?value=\"(.*?)\".?", response.text)
            if len(found) >= 1:
                for match in found:
                    if match[0] in ['vo', '--' ]:
                        self._data[match[0]] = match[1] # daten in dict updaten
                        self.logger.debug("RadioInet: gelesene Daten{0}{1}".format(match[0],match[1]))
                    
            #Search for the Stationurls
            self.logger.debug("RadioInet: Stationen")
            response = requests.get("http://"+self.device+"/de/stations.shtml")
            found = re.findall(r".? name=\"(.*?)\".*s.*?value=\"(.*?)\".?", response.text)
            for match in found:
                self.logger.debug("RadioInet: gelesene Daten{0} {1}".format(match[0],match[1]))
                self._stations[match[0]] = match[1]
                
            self.logger.debug("RadioInet: gelesene Daten in Stationsdict! {0}".format(self._stations))
        except OSError:
            self.logger.error("RadioInet: Fehlerbei der Datenabfrage von {}".format(self.device)) 
    def findStation(self):
        for station in self._stations:
            if self._stations[station] == self._data['--']:
                self.logger.info("RadioINet: Stationname found in saved Stations!{0} {1}".format(self._stations[station], self._data['--']))
                for items in self._itemlist:
                    if items[1] == station:
                        self.logger.info("RadioINet: Stationname found in Itemlist{0} {1}".format(items[1],station))
                        
                        for childs in items[0].return_children():
                            radio_function = self.get_iattr_value(childs.conf,'radio')
                            if radio_function[0] == 'p':
                                childs(True, 'RadioInet')
                            self.logger.info("RadioINet: Stationname found in Itemlist{0}".format(childs))
                      
                #radio_function = self.get_iattr_value(item.conf,'radio')
                #for function in radio_function:
                #    if function == station:
                #        self.logger.info("RadioINet: {0} {1}".format(station, self._data['--']))
                break
                
    ####
    ###UDP Commands
    ###
    
    def sendCommand(_command, _value,_id):
        """
        Sends a UDP Message to the Radio
        :param _command: 
        :param _value: 
        :param _id: specifie ID like shNG
        """
        if checkCommand(_command) == True:
            MESSAGE = "COMMAND:" + _command + "\r\n" + _value + "\r\nID:" + _id + "\r\n\r\n"
            self.logger.info("RadioINet: Send {0}".format(MESSAGE))

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            sock.sendto(MESSAGE.encode(), (UDP_IP, UDP_PORT))
            sock.close()
        else:
            self.logger.info("RadioINet:Command not supported")

    def checkCommand(_command):
        if _command in ['DISCOVER', 'GET', 'SET', 'PLAY', 'SAVE', 'REMOVE', 'RESET_BLOCK']:
            return True
        else:
            return False
