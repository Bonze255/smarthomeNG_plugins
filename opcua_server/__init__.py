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
import copy
from datetime import datetime
import time
from math import sin

import sys
sys.path.insert(0, "..")
import time

from opcua import ua, Server
from lib.model.smartplugin import SmartPlugin
from lib.logic import Logics

from opcua import ua
from opcua.common import events
from opcua import Node
# ----------------------------------------------------------------------------------------------
# Subscription Handler. To receive events from server for a subscription
# to change an item when on OPCUa-Server a Node is changed
# ----------------------------------------------------------------------------------------------
from opcua import ua, uamethod, Server    
class SubHandler(object):
    def __init__(self, object):
        self.object = object
    
    def datachange_notification(self, node, val, data):
        name = node.get_display_name().Text

        self.object.logger.debug("Python: NewDatachange Event!")
        self.object.change_item(self.object, name, val, data)        
# ----------------------------------------------------------------------------------------------
# Main Plugin Class
# ----------------------------------------------------------------------------------------------
class OPCua(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION="0.0.1"
    
    def __init__(self, smarthome,ip='127.0.0.1', path='smarthomeNG/server/',uri='www.smarthomeNG.de',name='smarthomeNG OPCua Server', read_cyl=60):
        # Plugin Configuration
        self._ip = str(ip)
        self._path = str(path)
        self._uri = str(uri)
        self._name = str(name)
        self._sh = smarthome
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._connected = False
        
        # Setup our server
        self._server = Server()
        self._server.set_security_policy([ua.SecurityPolicyType.NoSecurity])         
        self._server.set_endpoint("opc.tcp://"+ self._ip +":4840"+ self._path )
        self._server.set_server_name(self._name)
        
        ## setup our own namespace, not really necessary but should as spec
        self._idx = self._server.register_namespace(self._uri)
        
        ## get Objects node, this is where we should put our nodes
        self._objects = self._server.get_objects_node()
        
        # Create Item Object 
        self._myobject = self._objects.add_object(self._idx, "items")
        
        #########Start Plugin
        self.logger.debug("OPCua: Start Plugin!")
        

    # ----------------------------------------------------------------------------------------------
    # Logiken einlesen 
    # ----------------------------------------------------------------------------------------------    
    def parse_logic(self, logic):
        pass
    # ----------------------------------------------------------------------------------------------
    # Befehl senden, wird aufgerufen wenn sich item  mit robvac ändert!
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'OPCua':
            itemtype = item.type() 
            if itemtype == 'bool':
                pass
            children = self._myobject.get_children()
            self.logger.debug("OPCua: all children{}".format(self._myobject.get_children()))
            
            for child in children:
                #self.logger.debug("OPCua: Childs {}".format(child))
                this_child = self._server.get_node(child)
                #self.logger.debug("OPCua: this Child {}".format(this_child))
                name = this_child.get_display_name().Text
                #self.logger.debug("OPCua: this Child {}".format(name))
                if name == item.id():
                    this_child.set_value(item())
                    self.logger.debug("OPCua: Schreibe {0} an {1}".format(item(), item.id()))
                    break    
    
    def run(self):
        # ----------------------------------------------------------------------------------------------
        # Create Logics Object on Server
        # so Logics can called from OPCua Client
        # ----------------------------------------------------------------------------------------------
        self._logicobject = self._objects.add_object(self._idx, "logics")
        self.logics = Logics.get_instance()
        logiclist = self.logics.return_defined_logics()
        for logic in logiclist:
            self.logger.debug("OPCua: loaded Logic {}".format(logic))
            self._logicobject.add_method(self._idx, str(logic), self.logics.trigger_logic(logic))
        #######################################
        #Start Server
        try:
            self._server.start()
            self.logger.debug("OPCua: Server erfolgreich gestartet!")
            self.alive = True
        
            
        
            #Create Subscriptions all items 
            # keep track of the children of this object (in case python needs to write, or get more info from UA server)
            
            self.nodes = {}
            test = []
            for _child in self._myobject.get_children():
                _child_name = _child.get_browse_name()
                self.nodes[_child_name.Name] = _child
                test.append(_child)
            self.logger.debug("OPCua: subscripting {0}".format(self.nodes))
            # subscribe to properties/variables
            handler = SubHandler(self)
            sub = self._server.create_subscription(500, handler)
            handle = sub.subscribe_data_change(test)
            self.logger.debug("OPCua: subscripting {0} item {1} value {2}".format(handle, sub,self.nodes))

        except Exception as e:
            self.logger.debug("OPCua: Fehler beim starten des Servers {}".format(e))
            self.alive = False
        

    def stop(self):
        self.alive = False
        self._server.stop()
        
    def parse_item(self, item):
        if self.has_iattr(item.conf, 'opcua'):
            # populating our address space
            itempath = str(item.id())
            itemtype = item.type()
            value = item()
            
            if itemtype == 'bool':
                myvar = self._myobject.add_variable(self._idx, item.id(), item(), ua.VariantType.Boolean)
            elif itemtype == 'num':
                myvar = self._myobject.add_variable(self._idx, item.id(), item())
            elif itemtype == 'str':
                myvar = self._myobject.add_variable(self._idx, item.id(), item(), ua.VariantType.String)
            elif itemtype == 'list':
                myvar = self._myobject.add_variable(self._idx, item.id(), item())
            elif itemtype == 'dict':
                 myvar = self._myobject.add_variable(self._idx, item.id(),item())
            elif itemtype == 'foo':
                pass

            myvar.set_writable()    # Set MyVariable to be writable by clients
            self.logger.debug("OPCua: Found items idx{0} itemname {1} type{2} value {3}".format(self._idx, itempath, itemtype, value))

            return self.update_item
# ----------------------------------------------------------------------------------------------
# IS called by the Subscription Handler. 
# to change an item when the OPCUA Server Node is changed
# ----------------------------------------------------------------------------------------------            
            
    def change_item(self, node, name , val, data):
        self.logger.debug("OPCua: Item changed node {0} value {1} data {2}".format(name, val, data))
        #item = node.get_browse_name()
        
        for item in self._sh.items.return_items():
            if item.id() == name:
                item(val,'OPCua')
                self.logger.debug("OPCua: Item changed{0}".format(val))
                break
