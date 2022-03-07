#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################
#
#  Copyright 2020 Version-1.0.0    Manuel Holländer
#  Copyright 2021 Version-1.1.0    Manuel Holländer
####################################################################################

import logging
import threading
import struct
import binascii
import re
import time
import urllib
import doorbirdpy
import requests
from pathlib import Path

import os
import socket
import binhex
import sys
import json
import sys
import base64
from base64 import b64decode

from Crypto.Cipher import ChaCha20_Poly1305
import nacl.pwhash

from datetime import datetime

from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class Dbird(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.1.0"
    
    def __init__(self, smarthome,ip='127.0.0.1', username='', password='', read_cycle=120, image_path='',image_snapshots_dir='', image_motion_dir='',image_doorbell_dir='', max_files = 10, webserver_image_dir=''):
        self._ip = str(ip)
        self._username = str(username)
        self._password = str(password)
        self._max_files = int(max_files)
        self._cycle = int(read_cycle)
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        self._webserver_image_dir = str(webserver_image_dir)
        self._image_snapshots_dir = str(image_snapshots_dir)
        self._image_doorbell_dir = str(image_doorbell_dir)
        self._image_motion_dir = str(image_motion_dir)
        self._image_path = str(image_path)
        self._data = {}
        self.messages = {}
        self._lock = threading.Lock()
        self.retry_count_max = 3
        self.retry_count = 1
        self._connected = False
        self._udpport = 35344
        
        #OPen the UDP Port
        self.DoorbirdUDPServer = threading.Thread(target = self.UDPServer)
        self.DoorbirdUDPServer.start()
        
        if self._username == '' or self._password == '':
            self.logger.error("Doorbird: No Username/Password for Communication given, Plugin would not start!")
        else:
           
            
            if self._image_snapshots_dir == '':
                self.logger.debug("Doorbird: No snapshop dir given, use Cloud only!")
            if self._image_doorbell_dir == '':  
                self.logger.debug("Doorbird: No doorbell dir given, use Cloud only!")
            if self._image_motion_dir == '':   
                self.logger.debug("Doorbird: No motion dir given, use Cloud only!")
            
            self._doorbird = doorbirdpy.DoorBird(self._ip, self._username, self._password)
            self._sh.scheduler.add('Doorbird read cycle', self._read, prio=5, cycle=self._cycle)
            try:
                if self._doorbird.ready() == True:
                    self.logger.debug("Doorbird: Plugin Start!")
                    #Read static item data
                    self._data['info'] = self._doorbird.info()
                    
                    if len(self._data['info']) > 1:
                        self._data['firmware'] = self._data['info']['FIRMWARE']
                        self._data['build'] = int(self._data['info']['BUILD_NUMBER'])
                        self._data['wifi_mac'] = str(self._data['info']['WIFI_MAC_ADDR'])
                        self._data['relays'] = self._data['info']['RELAYS']
                        self._data['device_type'] = self._data['info']['DEVICE-TYPE']  
                    
                    self._data['live_audio'] = "http://"+self._ip+"/bha-api/audio-receive.cgi"
                    self._data['motion_sensor_state2'] = self._doorbird.motion_sensor_state()
                    self._data['doorbell_state2'] = self._doorbird.doorbell_state()
                    self._data['live_video'] = '<img width="75%" src = "'+self._doorbird.live_video_url+'">'
                    self._data['rtsp_live_video'] = '<img width="75%" src = "'+self._doorbird.rtsp_live_video_url+'">'
                    self._data['live_image'] = '<img width="75%" src = "'+self._doorbird.live_image_url+'">'
                    self._data['snapshot_images'] = self.get_files(self._image_snapshots_dir)
                    
                    
            except Exception as e:
                self.logger.error("Doorbird: Error {}".format(e))        
        if not self.init_webinterface():
            self._init_complete = False
            

    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, über SHNG bei item_Change
    # ----------------------------------------------------------------------------------------------
    def groupread(self, ga, dpt):
        pass
        
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, zyklisch
    # ----------------------------------------------------------------------------------------------     

    
    def _read(self):
        motion =[]
        doorbell = []

        
        try:
            self._data['info'] = self._doorbird.info()
            self.logger.debug("Doorbird: ready cycle {}".format(self._data['info']))
            #if len(self._data['info']) > 1:
            #    self._data['firmware'] = self._data['info']['FIRMWARE']
            #    self._data['build'] = int(self._data['info']['BUILD_NUMBER'])
            #    self._data['wifi_mac'] = str(self._data['info']['WIFI_MAC_ADDR'])
            #    self._data['relays'] = self._data['info']['RELAYS']
            #    self._data['device_type'] = self._data['info']['DEVICE-TYPE']  
            self._data['live_video'] = '<img width=75% src = "'+self._doorbird.live_video_url+'"/>'
            self._data['rtsp_live_video'] = '<img width=75% src = "'+self._doorbird.rtsp_live_video_url+'"/>'
            self._data['live_image'] = '<img width=75% src = "'+self._doorbird.live_image_url+'"/>'
            
            #Fix for other special devices
            self._data['doorbell_state2'] = self._doorbird.doorbell_state()
            self._data['motion_sensor_state2'] = self._doorbird.motion_sensor_state()
            
            if self._image_snapshots_dir != '':
                self._data['snapshot_images'] = self.get_files(self._image_snapshots_dir)
            else:
                self._data['snapshot_images'] = ""
           
            if self._image_doorbell_dir != '':  
                self._data['doorbell_images'] = self.get_files(self._image_doorbell_dir)
            else:
                for i in range(1,self._max_files ):
                    doorbell.append(self._doorbird.history_image_url(i, "doorbell"))
                self._data['doorbell_images'] = doorbell
            
            if self._image_motion_dir != '':   
                self._data['motion_images'] = self.get_files(self._image_motion_dir)
            else:
                for i in range(1,self._max_files ):
                    motion.append(self._doorbird.history_image_url(i, 'motionsensor'))
                self._data['motion_images'] = motion
            self._data['html_viewer'] = self._doorbird.html5_viewer_url
            
            
            ##Update Items
            self.update_items()
        except Exception as e:
                self.logger.error("Doorbird: Error {}".format(e))

    # ----------------------------------------------------------------------------------------------
    # Items mit liste self._data vergleichen und updaten 
    # ----------------------------------------------------------------------------------------------
    def update_items(self):
        for x in self._data:
            if x in self.messages:
                self.logger.debug("Doorbird: Update item {1} mit key {0} = {2}".format(x, self.messages[x], self._data[x]))
                item = self.messages[x]
                item(self._data[x], 'Doorbird')

    
    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit doorbird ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Dbird':
             if self.has_iattr(item.conf, 'doorbird'):
                message = self.get_iattr_value(item.conf, 'doorbird')
                value = item()
                if message == 'light_on':
                    if value == True:
                        item(False, 'Doorbird')
                        response = self._doorbird.turn_light_on()
                        self.logger.debug("Doorbird: Send MESSAGE {},  RESPONSE {} ".format(message, response))
                elif message == "relay1":
                    if value == True:
                        item(False, 'Doorbird')
                        response = self._doorbird.energize_relay(1)
                        self.logger.debug("Doorbird: Send MESSAGE {},  RESPONSE {} ".format(message, response))
                elif message == "relay2":
                    if value == True:
                        item(False, 'Doorbird')
                        response = self._doorbird.energize_relay(2)
                        self.logger.debug("Doorbird: Send MESSAGE {},  RESPONSE {} ".format(message, response))
                elif message == "snapshot":
                    if value == True:
                        item(False, 'Doorbird')
                        response = self.make_snapshot(self._image_snapshots_dir)
                        
                        self.get_files(self._image_snapshots_dir)#aufruf snapshot    
                        self.logger.debug("Doorbird: Send MESSAGE {},  RESPONSE {} ".format(message, response))
                elif message == "cleanup":
                    if value == True:
                        item(False, 'Doorbird')
                        self.cleanup_folder(self._image_snapshots_dir)
                        self.logger.debug("Doorbird: Cleaned up Snapshot Folder!")
    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'doorbird'):
            message = self.get_iattr_value(item.conf, 'doorbird')
            self.logger.debug("Doorbird: {0} keyword {1}".format(item, message))

            if not message in self.messages:
                self.messages[message] = item
                
            return self.update_item
    
    def update_item_read(self, item, caller=None, source=None, dest=None):
        if self.has_iattr(item.conf, 'doorbird'):
            for message in item.get_iattr_value(item.conf, 'doorbird'):
                self.logger.debug("Doorbird: update_item_read {0}".format(message))
            
    def make_snapshot(self, folder):
        """
        Make a Snapshotimage from video stream, and save it to given Folder
        """
        image_dir = os.path.join(self._image_path, folder)
        filename = Path(image_dir)
      
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        self.logger.debug("Doorbird: Make Snapshot: time {} path {}".format(timestamp,filename))
        if filename.exists():
            try:
                r = requests.get(self._doorbird.live_image_url, stream=True)
                
                if r.status_code == 200:
                    with open(str(image_dir)+str(timestamp)+".jpg","wb") as file:
                        for chunk in r.iter_content(1024):
                            file.write(chunk)
                else:
                    self.logger.debug("Doorbird: making Snapshot in {}  error ".format(folder))
            except Exception as err:
                self.logger.debug("Doorbird: error {}".format(err))
        else:
            self.logger.debug("Doorbird: Snapshot-Path {} does not exist!".format(filename))
        
        try:
            files = []
            self.logger.debug("Doorbird: delete filename {}".format(filename))
            for file in filename.glob('*.jpg'):
                files.append(os.path.join(filename,str(file.name)))
            self.delete_files(files)
            self.logger.debug("Doorbird: Try to Delete IN {}; while more than {} !".format(files)) 
            self.logger.debug("Doorbird: Try to Delete IN {}; while more than {} !".format(folder, self._max_files)) 
        except Exception as e:
            self.logger.debug("Doorbird: ERROR Try to Delete IN {}; while more than {} !, {}".format(folder, self._max_files,e))       
   
    def get_files(self, folder):
        """
        Get Files from given Folder
        """
        image_dir = os.path.join(self._image_path, folder)
        filename = Path(image_dir)
        self.logger.debug("Doorbird: filename {}".format(filename))
        #absolutpfad  zum script
        path = filename.absolute().as_uri()

        files = []
        if filename.exists():
            try:
                for file in filename.glob('*.jpg'):
                    files.append(self._webserver_image_dir+folder+str(file.name)+'')
                    #self.logger.debug("Doorbird: Snapshot-FIle found {}".format(file.name))
                files.sort(reverse=True)
                if len(files)>0:
                    self.logger.debug("Doorbird: Found files {}".format(files))
                    #self._data['snapshot_images'] = files
                    #self.delete_files(files)
                    return files
                else:
                    return []
            except Exception as err:
                
                self.logger.debug("Doorbird: error {}".format(err))
        else:
            self.logger.debug("Doorbird: Snapshot-Path does not exist!")
            return []
            
    def delete_files(self, files):
        """
        Delete files when more than max_files in the given folder
        """
        files.sort(reverse=True)

        #delete older files!
        if len(files) > self._max_files:
            for file in range(self._max_files, len(files)):
                filepath = Path(files[file])
                self.logger.debug("Doorbird: Try to Delete IN {} - {};".format(file, filepath))       
                filepath.unlink()
        return files
        
    def cleanup_folder(self, folder):
        """
        Delete all Files from a given folder
        """
        image_dir = os.path.join(self._image_path, folder)
        filename = Path(image_dir)
        for file in filename.glob('*.jpg'):
            self.logger.debug("Doorbird: Found file {}".format(file))
            file.unlink()
        
    def decrypt(self, payload):
        """
        Decrypt given Payload
        """
        if len (payload) >= 70:
        
            ident, version,oplimit,mlimit,salt,nonce,ciphertext = struct.unpack(">3sBll16s8s34s",payload)
            self.logger.debug("Doorbird: ident{}, version{}, oplimit{}, mlimit{}, salt{}, nonce{}, ciphertext{}".format(ident, version, oplimit, mlimit, salt, nonce, ciphertext))
            #ident =     payload[:3]     #3  \xDE\xAD\xBE
            base64_bytes = base64.b64encode(ident)
            self.logger.debug("Doorbird: base64_bytes {}".format(base64_bytes.decode('ascii')))
            if base64_bytes.decode('ascii') == '3q2+' and len(salt) == 16:
                self.logger.debug("Doorbird: Ready to decrypt")
                streched = nacl.pwhash.argon2i.kdf(32,self._password[:5].encode('utf'), salt, opslimit=oplimit, memlimit=mlimit,encoder=nacl.encoding.RawEncoder)
                cipher = ChaCha20_Poly1305.new(key=streched, nonce=nonce)
                plaintext = cipher.decrypt(ciphertext)
                decrypted_user= (struct.unpack(">6s",plaintext[:6])[0]).decode()
                #Username check
                if decrypted_user == self._username[:6]:
                    try:
                        decrypted_event = (struct.unpack(">8s",plaintext[6:14])[0].strip()).decode()
                        timestamp = struct.unpack(">L",plaintext[14:18])[0]
                        self._data['event_time'] = datetime.fromtimestamp(timestamp+(3600*1))##convert it to MEZ
                    except Exception as e:
                        self.logger.info("Doorbird: Error maybe wrong user? {}".format(e))
                        return False
                    
                    if decrypted_event == 'motion': 
                        self._motionAction()
                    elif decrypted_event.isnumeric():
                        #kompaktklingelanlagen 1-2-3 Tasten
                        if int(decrypted_event) < '100':
                            self._data['triggernumber'] = int(decrypted_event)
                        #mehrtastenmodule ab 10 Tasten
                        elif int(decrypted_event) >= '100':
                            self._data['triggernumber'] = int(decrypted_event[1:])
                        
                        self._doorbellAction()
                        
                    self.logger.info("Doorbird: User {} triggered, while {} at {}".format(decrypted_user,decrypted_event,self._data['event_time']))
                    self.update_items()
                    self._data['motion_sensor_state'] = False
                    self._data['doorbell_state'] = False
                
            else:
                self.logger.debug("Doorbird: Falscher Header")
                return False
                
    def UDPServer(self):
        """
        Start a UDP Server from given port
        """
        ip=''
        self.logger.debug("Doorbird: Opening UDP Port")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Create Datagram Socket (UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 5) # Allow incoming broadcasts
        s.setblocking(True) # Set socket to blocking mode
        s.bind((ip, self._udpport)) #Accept Connections on port
        while True:
            try:
                message, adress= s.recvfrom(2048) # Buffer size is 8192. Change as needed.
                try:
                    self.decrypt(message)
                except Exception as e:
                    self.logger.debug("Doorbird: Cannot Decrypt {}".format(e))
            except Exception as e:
                self.logger.debug("Doorbird: UDP Server Cannot connect.{}".format(e))

    def _motionAction(self):
        """
        when the motion is detected
        """
        self.logger.info("Doorbird: Motion trigger erkannt")
        self._data['motion_sensor_state'] = True
        if self._image_doorbell_dir != "":
            self.make_snapshot(self._image_motion_dir)

        
    def _doorbellAction(self):
        """
        when the doorbell is triggered
        """
        self.logger.info("Doorbird: Doorbell trigger erkannt")
        self._data['doorbell_state'] = True 
        
        if self._image_doorbell_dir != "":
            self.make_snapshot(self._image_doorbell_dir)

# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------   

    def get_connection_info(self):
        info = {}
        info['ip'] = self._ip
        info['username'] = self._username
        info['password'] = self._password
        info['cycle'] = self._cycle
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
        
        self.logger.debug("Doorbird Plugin Debug ausgabe '{0}': {1}, {2}, {3}, {4}, {5}".format(self.get_shortname(), webif_dir, self.get_shortname(),config,  self.get_classname(), self.get_instance_name()))
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
        self.logger.debug("Doorbird Plugin : Init Webif")
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
            if ('doorbird' in item.conf):
                plgitems.append(item)
        self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), 
                            plugin_version=self.plugin.get_version(),
                            plugin_info=self.plugin.get_info(),
                            p=self.plugin,
                            connection = self.plugin.get_connection_info(),
                            webif_dir = self.webif_dir,
                            image_snapshots = self.plugin.get_files(self.plugin._image_snapshots_dir),
                            items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
                            
