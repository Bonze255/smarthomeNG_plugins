#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################
#
#  Copyright 2020 Version-1    Manuel Holländer

####################################################################################
####################################################################################
#
#   VERSION - 1
#
####################################################################################
# 
import logging
import requests
import json 
import threading

from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items

class Waqi(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="1.0.0"
    
    def __init__(self, smarthome,city='/', token='',cycle=20, alarm=150, keys =''):
        self._city= str(city)
        self._cycle = int(cycle)
        self._token = str(token)
        self._alarm = int(alarm)
        self._keys = keys
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        self.messages = {}
        self._lock = threading.Lock()
        self.firstrun = True
        self.base_url = "https://api.waqi.info"
        self._read()
        
        self._sh.scheduler.add('Waqi read cycle', self._read, prio=5, cycle=self._cycle)
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
        self._data = {}
        self._data['data'] = {}
        try:
            r = requests.get(self.base_url + f"/feed/"+self._city+"/?token="+self._token)
            
            if r.status_code == 200:
                if len(r.json()['data']['iaqi'].keys())>0:
                    for key in r.json()['data']['iaqi']:
                        self.logger.debug("Waqi: request {}".format(key))
                        self._data[key] = int(r.json()['data']['iaqi'][key]['v'])
                        self._data['data'][key] = int(r.json()['data']['iaqi'][key]['v'])
                        
                    self._data['aqi'] = int(r.json()['data']['aqi'])
                    self._data['city'] = str(r.json()['data']['city']['name'])
                    self._data['data']['aqi'] = int(r.json()['data']['aqi'])
                    self._data['data']['city'] = str(r.json()['data']['city']['name'])
                    
                    
                    if self._data['aqi'] >= int(self._alarm):
                        self._data['aqi_alarm'] = True
                    else:
                        self._data['aqi_alarm'] = False
                        
                    if (    ('pm25' in self._data.keys()) and (self._data['pm25'] >= self._alarm)   ):
                        self._data['pm25_alarm'] = True
                    else:
                        self._data['pm25_alarm'] = False
                        
                    if(('o3' in self._data.keys()) and (self._data['o3'] >= self._alarm)  ):
                        self._data['o3_alarm'] = True
                    else:
                        self._data['o3_alarm'] = False
                        
                    if (('no2' in self._data.keys()) and (self._data['no2'] >= self._alarm)    ):
                        self._data['no2_alarm'] = True
                    else:
                        self._data['no2_alarm'] = False
                    
                    if (('so2' in self._data.keys()) and (self._data['so2'] >= self._alarm)    ):
                        self._data['so2_alarm'] = True
                    else:
                        self._data['so2_alarm'] = False 
                    
                    
                    #forecast
                    for key in r.json()['data']['forecast']['daily']:
                        self.logger.debug("Waqi: request {}".format(key))
                        for i in range(0, len(r.json()['data']['forecast']['daily'][key])):
                            self._data['forecast_'+key+'_'+str(i)+'_min'] = int(r.json()['data']['forecast']['daily'][key][i]['min'])
                            self._data['forecast_'+key+'_'+str(i)+'_max'] = int(r.json()['data']['forecast']['daily'][key][i]['max'])
                            self._data['forecast_'+key+'_'+str(i)+'_avg'] = int(r.json()['data']['forecast']['daily'][key][i]['avg'])
                            self._data['forecast_'+key+'_'+str(i)+'_date'] = r.json()['data']['forecast']['daily'][key][i]['day']
                    
                    self.logger.debug("Waqi: Read data {}".format(self._data))
            else:
                self.logger.debug("Waqi: data{}".format(r.json()))
                self.logger.error("Waqi: Reading ERROR from Waqi")
        except Exception as e:
                self.logger.error("Waqi: Error {}".format(e))
        #resort data
        resorted = {}
        for key in sorted(self._data['data'].keys()):
            #Filterung, nach gewunschten Werte zum widget
            if key in self._keys or self._keys =='':
                resorted[key] = self._data['data'][key]
        self._data['data'] = resorted
            
        for x in self._data:
            if x in self.messages:
                self.logger.debug("Waqi: Update item {1} mit key {0} = {2}".format(x, self.messages[x], self._data[x]))
                item = self.messages[x]
                item(self._data[x], 'Waqi')
                
    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit robvac ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'Waqi':
             pass
    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False
        
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'waqi'):
            message = self.get_iattr_value(item.conf, 'waqi')
            self.logger.debug("Waqi: {0} keyword {1}".format(item, message))

            if not message in self.messages:
                self.messages[message] = item
                
            return self.update_item
    
    def update_item_read(self, item, caller=None, source=None, dest=None):
        if self.has_iattr(item.conf, 'waqi'):
            for message in item.get_iattr_value(item.conf, 'waqi'):

                self.logger.debug("Waqi: update_item_read {0}".format(message))
            
# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------   
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
        
        self.logger.debug("Plugin Debug ausgabe '{0}': {1}, {2}, {3}, {4}, {5}".format(self.get_shortname(), webif_dir, self.get_shortname(),config,  self.get_classname(), self.get_instance_name()))
        # Register the web interface as a cherrypy app
        self.mod_http.register_webif(WebInterface(webif_dir, self),
                                     self.get_shortname(),
                                     config,
                                     self.get_classname(), self.get_instance_name(),
                                     description='')

        return True

# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------   

    def get_connection_info(self):
        info = {}
        info['city'] = self._city
        info['token'] = self._token
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
        
        self.logger.debug("Plugin Debug ausgabe '{0}': {1}, {2}, {3}, {4}, {5}".format(self.get_shortname(), webif_dir, self.get_shortname(),config,  self.get_classname(), self.get_instance_name()))
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
            if ('waqi' in item.conf):
                plgitems.append(item)
        self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(), 
                            plugin_version=self.plugin.get_version(),
                            plugin_info=self.plugin.get_info(),
                            p=self.plugin,
                            connection = self.plugin.get_connection_info(),
                            webif_dir = self.webif_dir,
                            #image_snapshots = self.plugin.get_files(),
                            items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
                            
