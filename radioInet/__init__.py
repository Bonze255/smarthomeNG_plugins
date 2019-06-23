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
# importing the requests library
import requests
import socket
import struct
import binascii


from lib.logic import Logics
from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class radioinet(SmartPlugin):
    """
    Main class of the Modbus TCP-Plugin. Does all plugin specific stuff and provides
    the update functions for the items
    """
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"
    
    # Initialize connection
    def __init__(self, smarthome, device='', cycle='5', item_subtree=''):
        """
        Initalizes the plugin. The parameters described for this method are pulled from the entry in plugin.yaml.

        :param sh:                 The instance of the smarthome object, save it for later references
        :param ip:                 hostip
        :param cycle:              number of seconds between updates
        """
       
        self.logger = logging.getLogger(__name__)
        self.device = device
        if self.device  == '':
            self.logger.error("Radio Inet: No Device Ip specified, plugin is not starting")
            return
        self.port = 4244

        self.cycle = int(cycle)
        if self.cycle =='':
            self.logger.info("Radio Inet: No Cycle specified, default 10s is used")
            self.cycle = 10
            
        self.item_subtree = str(item_subtree)
        if self.item_subtree == '':
            self.logger.warning("RadioInet: item_subtree is not configured, searching complete item-tree instead. Please configure item_subtree to reduce processing overhead" )   
        
        self._sh = smarthome

        #Listen
        self._itemlist = []                 #puffert die benutzen Radio Items
        self.keys ={'GET':['POWER_STATUS', 'INFO_BLOCK','ALARM_STATUS','VOLUME','PLAYING_MODE','ALL_STATIONS_INFO','TUNEIN_PARTNER_ID', 'ENERGY_MODE'],
                    'SET':['RADIO_ON', 'RADIO_OFF', 'VOLUME_ABSOLUTE','VOLUME_INC','VOLUME_DEC','VOLUME_MUTE','VOLUME_UNMUTE','ALARM_OFF','ALARM_SNOOZE','ALARM'],
                    'PLAY':['STATION','UPNP','AUX','TUNEIN_INIT','TUNEIN_PLAY']#,
                    #'SAVE':['STATION', 'TUNEIN_FAVORITE']
                    }
        #mute = VOlume_ABSolue = -1
        self.data = {}
        self.config = { #enthält die configdaten
            'ah':'08', #alarmzeitstunden 0-23
            'am':'00',           #alarmzeitminuten 0-59
            'bb':100,         #backgroundlight 0-100
            'bl':1,             #backlight 0-2
            'dm':0,             #lcdmodus 0-2
            'ea':0,             #alarm 0-1
            'hr':'18',           #stunden 0-23
            'mi':'45',           #minuten 0-59
            'ln':'de',                #sprache de,fr,en,pl
            'ms':1,             #audiomodus 0-1
            'sm':0,             #soundmodus 0-5
            'sp':0,             #netzspannung 0-1
            'ss':'00',           #timerzeit 0-60
            'et':'00',            #kurzzeittimer
            'st':'00',            #kurzzeittimerzeit
            'es':'00',            #sleeptimer
            'sw':0,             #schaltfunktion
            'tz':'+1',            #zeitdifferenz
            'zs':0,              #zeitzone
            'vo':0,              #lauststaerke
            'vo_tag':10,#lautstaerke am tage
            'vo_nacht': 5,#lautstaerke bei Nachtitem
            'nacht':False}
        self._stations = {} #enthält die stationsangaben
        self.logger.info("RadioInet: starting")
        
        #Read first TIme all Configuration Settings
        #UDP SERVER THREAD
        self.UDPServerThread = threading.Thread(target = self.UDPServer)
        self.UDPServerThread.start()
        
        self.sendUDP('GET', 'ALL_STATIONS_INFO')
        
        if not self.init_webinterface():
            self._init_complete = False
            
    def connect(self):
        pass
    def disconnect(self):
        pass
    def run(self):
        self.alive = True
        
    def stop(self):
        self.alive = False
        self.UDPServerThread.stop()
        
    def parse_item(self, item):
        # check for smarthome.py attribute 'radio' in yaml
        if self.has_iattr(item.conf, 'radio'):
            radio_function = self.get_iattr_value(item.conf,'radio')
            self._itemlist.append([item, radio_function, item()])
            self.logger.info("RadioInet: parse Radio_inet item: {0} , Function {1}, Value {2}".format(item, radio_function,item()))
            return self.update_item
        
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'RadioInet':
            self.logger.info("RadioInet: Es hat sich ein Item{0} geändert, paramter ist in den Rahmenwerten, zu Radio senden".format(item))
            
            radio_function = self.get_iattr_value(item.conf,'radio')
            #neuer wert zuweisen
            #self._data[radio_function] = item()
            self.sendUDP(radio_function, item())
          

    def sendUDP(self, _command, _payload):
        _id = 'shNG'
        for key in self.keys.keys():
            if _command in self.keys[key]:
               print("Command from keylist ",self.keys[key])
               print("KEY ",key)
               break
               
        if _command == 'VOLUME_ABSOLUTE' or _command == 'STATION':
            _command = _command +':' + str(_payload)
           
        MESSAGE = "COMMAND:" + key + "\r\n" + _command + "\r\nID:" + _id + "\r\n\r\n"
        print("RadioINet: Send MESSAGE{0}".format(MESSAGE))

        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
        sock.sendto(MESSAGE.encode(), ('192.168.178.52', 4244))
        sock.close()
        
    def UDPMessageParser(self,_message):
        message = _message.splitlines()
        print("COMPLETE MESSAGE",message)
        if 'NACK' not in message[4]:#and 'SET' not in message[0]:

            request = message[0].split(':')[1] #GET/SET
            command = message[1] #INFO_BLOCK
            id = message[2].split(':')[1] #shNG
            payload = message[3:len(message)]
            
            self.logger.debug("RadioINet: REQUEST {} ".format(request))
            self.logger.debug("RadioINet: Command {} ".format(command))
            self.logger.debug("RadioINet: id {}".format(id))
            self.logger.debug("RadioINet:payload {}".format( payload))
            payload_list = {}
            channel =[]
            all_channels = {}
            if message[2] !='shNG': #NUR wenn befehle durch anderen Teilnehmer verursacht
                if 'ALL_STATION_INFO' in message[1]:#komplette channels in Speicher
                  ##die antwort wird immer ab payload3-schluss-2 gesendet! 
                    for i in range(3, len(message)-2, 3):
                        channel = {}
                        for i2 in range(0,3):
                          if ':' in message[i+i2]:
                            key, value = message[i+i2].split(':',1)
                            if "CHANNEL" in key:
                                channelkey = "CHANNEL"+value
                                stationindex = value
                            else:
                                channel[key+str(stationindex)] = value

                                all_channels[key+str(stationindex)] = value
                                payload_list[channelkey] = channel
                                self.logger.debug("RadioInet: CHANNEL LIST {}".format(all_channels))
                else:##aktuell gespielt
                    channel = {}
                    for i in range(3,len(message)-2):
                      if ':' in message[i]:
                        key, value = message[i].split(':',1)
                        channel[key] = value
                    self.logger.debug("RadioINet: PAYLOAD LIST{} ".format(channel))
                    self.change_item(channel)
                    
    """Sets the Item with radio value to the specific value"""                
    def change_item(self, payload):
        self.logger.debug("RadioInet: change_item{0}".format(payload))
        new_value = None
        for payloadkey in payload.keys():

            for item in self._sh.items.return_items():
                if self.has_iattr(item.conf, 'radio'):
                    itemkey = item.conf['radio']
                    
                    
                    if payloadkey == itemkey:
                        self.logger.debug("RadioInet: item {} erkannter Key {} payload {}".format(item, payloadkey,payload[payloadkey]))
                        if payload[payloadkey] == 'ON':
                            new_value = True
                        elif payload[payloadkey] == 'OFF':
                            new_value = False
                        elif payloadkey == 'NAME' or payloadkey == 'URL':
                            new_value = str(payload[payloadkey])
                        else:
                            new_value = int(payload[payloadkey])
                        item(new_value,'RadioInet')
                        #break
                        self.logger.debug("RadioInet: Item {0} - {1} changed to {2}".format(item, item(), new_value))
                #break    
   # def makeRequest(self,_url,_type, _param):
   #     if _type == 'get':
   #         if _param != '':
   #             response = requests.get(url = _url, params = _param)
   #         else:
   #             response = requests.get(url = _url)
   #     elif _type == 'post':
   #         response = requests.post(url = _url, data = _param)
   #     
   #     if response.status_code > 200:
   #         self.logger.debug("RadioINet: Fehler beim Senden des Befehls an das Radio {}".format(response.status_code))
   #         return False
   #     else:
   #         self.logger.info("RadioINet: Befehl OK {}".format(response.status_code)) 
   #         #self.logger.debug("RadioINet: {}".format(response.text)) 
   #         return response


    ####
    ###UDP Commands
    ###
 
   # def sendCommand(_command, _value,_id):
    #    """
   #     Sends a UDP Message to the Radio
    #    :param _command: 
   #     :param _value: 
   #     :param _id: specifie ID like shNG
    #    """
   #     if checkCommand(_command) == True:
    #        MESSAGE = "COMMAND:" + _command + "\r\n" + _value + "\r\nID:" + _id + "\r\n\r\n"
    #        self.logger.info("RadioINet: Send {0}".format(MESSAGE))

     #       sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
     #       sock.sendto(MESSAGE.encode(), ('192.168.178.52', 4244))
     #       sock.close()
     #   else:
     #       self.logger.info("RadioINet:Command not supported")

    def UDPServer(self):
        port = 4242
        ip=''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Create Datagram Socket (UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow incoming broadcasts
        s.setblocking(False) # Set socket to non-blocking mode
        s.bind(('', port)) #Accept Connections on port
        while True:
            try:
                message, address = s.recvfrom(8192) # Buffer size is 8192. Change as needed.
                print('message',message)
                self.UDPMessageParser(message.decode("utf-8") )
            except Exception as e:
                self.logger.info("RadioINet: Cannot connect.",e)
                
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
            if ('radio' in item.conf):
                plgitems.append(item)
        self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), 
                            plugin_version=self.plugin.get_version(),
                            plugin_info=self.plugin.get_info(),
                            p=self.plugin,
                            config = self.plugin.config,
                            webif_dir = self.webif_dir ,
                            items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
                            
    #@cherrypy.expose
    #def action(self, name=None):
    #    self.logger.debug("Plugin {0}: CherryPi Call action {1}".format(self.plugin, name))
    #    if name == 'stop':
    #        self.plugin.set_cpu_status("stop")
    #    elif name == 'warmstart':
    #        self.plugin.set_cpu_status("warmstart")
    #    elif name == 'coldstart':
    #        self.plugin.set_cpu_status("coldstart")
