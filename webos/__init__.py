
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

import pywebostv

from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class LGWebos(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="0.0.1"
    
    def __init__(self, smarthome,ip='127.0.0.1', name='', password=''):
        self._ip = str(ip)
        self._name = str(name)
        self._password = str(password)
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        self._store = {} #for the registration process
        
        self._lock = threading.Lock()
        
        if self._ip == '':
            self._client = WebOSClient.discover()[0]
            
        else:
            self._client = WebOSClient(self._ip)
        finally:
            self._client.connect()
            self.logger.debug("LGWebos: Plugin Start!")
            
            for self._status in self._client.register(self._store):
                if self._status == self._client.PROMPTED:
                    self.logger.info("LGWebos: Please accept the connect on the TV!")
                elif self._status == self._client.REGISTERED:
                    self._connected = True
                    self._media = MediaControl(self._client)
                    self._system = SystemControl(self._client)
                    self._app =  ApplicationControl(self._client)
                    self._apps = self._app.list_apps()  
                    self.logger.info("LGWebos: Registration successful!")
      
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

        try:
            #do something cyclie
           
            
            for x in data:
                if x in self.messages:
                    self.logger.debug("LGWebos: Update item {1} mit key {0} = {2}".format(x, self.messages[x], data[x]))
                    item = self.messages[x]
                    item(data[x], 'LGWebos')
            
            
            pass
        except Exception as e:
                self.logger.error("LGWebos: Error {}".format(e))

        

    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit LGWebos ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'LGWebos':
           
            if self.has_iattr(item.conf, 'lgwebos'):
                message = self.get_iattr_value(item.conf, 'lgwebos')
                if message == "power_off":
                    self._system.power_off()
                    item(False, 'LGWebos') #reset Value 
                elif message == "notify":
                    self._system.notify(message)
                    item('', 'LGWebos') #reset Value 
                elif message == "system_info":
                    self._system.info()
                    item('', 'LGWebos') #reset Value 
                elif message == "launch_app":
                    self._media.stop()
                    item(False, 'LGWebos') #reset Value 
                elif message == "play":
                    self._media.play()
                    item(False, 'LGWebos') #reset Value 
                elif message == "pause":
                    self._media.pause()
                    item(False, 'LGWebos') #reset Value 
                elif message == "stop":
                    self._media.stop()
                    item(False, 'LGWebos') #reset Value 
                elif message == "rewind":
                    self._media.rewind()
                    item(False, 'LGWebos') #reset Value 
                elif message == "fast_forward":
                    self._media.fast_forward()
                    item(False, 'LGWebos') #reset Value 
                elif message == "volume_up":
                    self._media.volume_up()
                    item(False, 'LGWebos') #reset Value 
                elif message == "volume_down":
                    self._media.volume_down()
                    item(False, 'LGWebos') #reset Value 
                elif message == "set_volume":
                    self._media.set_volume(message)
                elif message == "set_mute":
                    self._media.set_volume(message)
                    item(False, 'LGWebos') #reset Value 
                elif message == "channel_up":
                    item(False, 'LGWebos') #reset Value 
                    self._media.channel_up()
                elif message == "channel_down":
                    self._media.channel_down()
                    item(False, 'LGWebos') #reset Value
                elif "play_youtube" in message:
                    #play_youtube|url
                    url = message.split('|')[1]
                    launch_info = self._app.launch(yt, content_id=url)
                    #item('', 'LGWebos') #reset Value 
                pass

    #Search for items with lgwebos attribute 
    #item key for the plugin is lgwebos    
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'lgwebos'):
            message = self.get_iattr_value(item.conf, 'lgwebos')
            self.logger.debug("LGWebos: {0} keyword {1}".format(item, message))

            if not message in self.messages:
                self.messages[message] = item
                
            return self.update_item 
            
    def run(self):
        self.alive = True
        self.logger.debug("LGWebos: Found items{}".format(self.messages))
        
    def stop(self):
        self.alive = False
        


    def update_item_read(self, item, caller=None, source=None, dest=None):
        if self.has_iattr(item.conf, 'lgwebos'):
            for message in item.get_iattr_value(item.conf, 'lgwebos'):
                self.logger.debug("LGWebos: update_item_read {0}".format(message))

# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------   

    def get_connection_info(self):
        info = {}
        info['ip'] = self._ip
        info['cycle'] = self._cycle
        info['paired'] = self._connected
        info['status'] = self._status
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
        self.logger.debug("Plugin : Init LGWebos")
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
                            
