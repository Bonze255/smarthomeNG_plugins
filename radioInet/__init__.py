#
#!/usr/bin/env python3
# vim: set encoding=utf-8 tabstop=4 softtabstop=4 shiftwidth=4 expandtab
#
####################################################################################
######################################################################################
#
#  Copyright 2021 Version-1    Manuel Holländer

####################################################################################
from jinja2 import Environment, FileSystemLoader
import cherrypy
import socket
import logging
import threading
import logging

from lib.model.smartplugin import *
from lib.module import Modules
from lib.item import Items
from math import floor


class RadioInet(SmartPlugin):
    ALLOW_MULTIINSTANCE = False
    PLUGIN_VERSION = "1.0.0"

    def __init__(self, smarthome, ip='127.0.0.1', name='shNG', cycle='50'):
        self._ip = str(ip)
        self._name = str(name)
        self._cycle = int(cycle)
        self._sh = smarthome
        self.stations = {}
        self.radioData = {}
        self.itemlist = {}  # keyword: item
        self.messages = {}
        self.logger = logging.getLogger(__name__)

        if not self.init_webinterface():
            self._init_complete = False

        self.logger.debug("RadioInet: Plugin Start!")
        if self._cycle > 30:
            self._sh.scheduler.add(
                'RadioInet: Ping Radio', self._read, prio=5, cycle=self._cycle)
        else:
            self.logger.warning(
                "RadioInet: Read Cycle is to fast! < 30s, not starting!")

        self.UDPServerInst = threading.Thread(target=self.UDPServer)
        self.UDPServerInst.start()
        # try to read playing status , when shNG is loaded after radioInet has fired some events
        try:
            self.sendCommand(self.msgBuilder('PLAYING_MODE'))
        except Exception as e:
            self.logger.debug(
                "RadioINet:Error sending through UDP! {}".format(e))
    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, über SHNG bei item_Change
    # ----------------------------------------------------------------------------------------------

    def groupread(self, ga, dpt):
        pass

    # ----------------------------------------------------------------------------------------------
    # Daten Lesen, zyklisch
    # ----------------------------------------------------------------------------------------------
    def _read(self):
        # self.sendCommand(self.msgBuilder('PLAYING_MODE'))
        self.sendCommand(self.msgBuilder('POWER_STATUS'))
        # self.sendCommand(self.msgBuilder('VOLUME'))
        pass
    # ----------------------------------------------------------------------------------------------
    # ->Items updaten mit actual data durch plugin!
    # ----------------------------------------------------------------------------------------------

    def update_items(self):
        self.logger.debug("RadioInet: Update item {} mit key {}".format(
            self.messages, self.radioData))
        for data in self.radioData:
            if data in self.messages:
                self.logger.debug("RadioInet: Update item {1} mit key {0} = {2}".format(
                    data, self.messages[data], self.radioData[data]))
                item = self.messages[data]
                item(self.radioData[data], 'RadioInet')

    # ----------------------------------------------------------------------------------------------
    # items ->dict #wenn item upgedatet wird neu values holen, durch extern
    # ----------------------------------------------------------------------------------------------
    def update_item(self, item, caller=None, source=None, dest=None):
        if caller != 'RadioInet':
            if self.has_iattr(item.conf, 'radioInet'):
                message = self.get_iattr_value(item.conf, 'radioInet')

                # boollsche items zurücksetzen
                if message == "VOLUME_INC":
                    item(False, 'RadioInet')
                elif message == "VOLUME_DEC":
                    item(False, 'RadioInet')
                elif message == "VOLUME":
                    message = "VOLUME_ABS"
                else:
                    pass
                value = item()

                # save a Station
                if message in ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8'] or message in ['n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8']:
                    id = message[1]
                    if 's' in message:
                        s = self.messages[message]()
                        n = self.messages['n'+str(id)]()
                    else:
                        n = self.messages[message]()
                        s = self.messages['s'+str(id)]()

                    message = 'SAVE_STATION'
                    value = [id, n, s]

                self.logger.debug(
                    "RadioInet: item {} mit value {} has changed!".format(message, value))
                self.sendCommand(self.msgBuilder(message, value))

    def run(self):
        self.alive = True

    def stop(self):
        self.alive = False

    def parse_item(self, item):
        if self.has_iattr(item.conf, 'radioInet'):
            message = self.get_iattr_value(item.conf, 'radioInet')
            self.logger.debug(
                "RadioInet: {0} keyword {1}".format(item, message))

            if not message in self.messages:
                self.messages[message] = item

            return self.update_item

      #UDP######################################################################
    def sendCommand(self, msg):
        """
        Sends a UDP Message to the Radio
        """
        port = 4244
        try:
            self.logger.debug("RadioINet: Send {0}".format(msg))

            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # UDP
            ret = sock.sendto(msg.encode(), (self._ip, port))
            # print(ret)
            sock.close()
            self.msg = ""
        except Exception as e:
            self.logger.debug(
                "RadioINet:Error sending through UDP! {}".format(e))

    def msgBuilder(self, key, value=None):
        """
        generates from the  items/keywords a msg which can send to the Radio
        :key from Item
        :value from item
        """
        # Direkt Commands
        discover = 'DISCOVER'
        userdefined = ['CHANGE_STATION']
        get = ['POWER_STATUS', 'INFO_BLOCK', 'ALARM_STATUS', 'VOLUME',
               'PLAYING_MODE', 'ALL_STATION_INFO', 'TUNEIN_PARTNER_ID']
        set = ['RADIO_POWER', 'VOLUME_ABS', 'VOLUME_INC',
               'VOLUME_DEC', 'VOLUME_MUTE', 'ALARM_OFF', 'ALARM_SNOOZE']
        play = ['PLAY_STATION', 'UPNP', 'AUX', 'TUNEIN_INIT', 'TUNEIN_PLAY']
        save = ['SAVE_STATION']
        # indirekte commands
        stations = ['s1', 's2', 's3', 's4', 's5', 's6', 's7', 's8']
        urls = ['n1', 'n2', 'n3', 'n4', 'n5', 'n6', 'n7', 'n8']
        try:
            key = key.upper()
            if key in discover:
                msg = key
                pass
            if key in get:
                msg = 'GET\r\n'+key
                self.logger.debug("RadioInet: GET Message {}".format(key))
                pass
            elif key in set:
                if key == 'RADIO_POWER':
                    if value == True or value == 'true':
                        msg = 'RADIO_ON'
                    else:
                        msg = 'RADIO_OFF'

                elif key == 'VOLUME_ABS':
                    # gets a procentual val 100=31 0=0
                    volume = floor((int(value)/3.22))
                    msg = "VOLUME_ABSOLUTE:" + str(volume)

                elif key == 'VOLUME_MUTE':
                    if value == True:
                        msg = 'VOLUME_MUTE'
                    else:
                        msg = 'VOLUME_UNMUTE'
                    #msg = key
                else:
                    msg = key
                pass

                msg = 'SET\r\n'+msg

            elif key in play:
                if key == 'PLAY_STATION':
                    msg = 'PLAY\r\nSTATION:'+str(value)
                elif key == 'TUNEIN_PLAY':
                    msg = 'TUNEIN:\r\nURL:' + \
                        str(value[0])+'\r\n TEXT:' + str(value[1])
                else:
                    msg = key
                    pass
            elif key in save:
                if key == 'SAVE_STATION':
                    msg = 'SAVE\r\nSTATION\r\nCHANNEL:' + \
                        value[0]+'\r\nNAME:'+value[1]+'\r\nURL:'+value[2]
                pass

            elif key in stations or key in urls:
                # daten  aus self.data muss nocha angepasst werden
                # passende andere daten suchen vom jeweiligen sender und telegrammzusammenbauen
                # number = key[1] #sendernummer
                value = []
                value.append = key[1]
                for item in sh.items.return_items():
                    if self.has_iattr(item.conf, 'radioInet'):
                        val = self.get_iattr_value(item.conf, 'radioInet')
                        if val == 's' + str(value[0]):
                            value.append = item()
                            if self.get_iattr_value(item.conf, 'radioInet') == 'n' + str(value[0]):
                                value.append = item()

                    msg = 'SAVE\r\nSTATION\r\nCHANNEL:' + \
                        value[0]+'\r\nNAME:'+value[1]+'\r\nURL:'+value[2]
            elif key in userdefined:
                if key == 'CHANGE_STATION':
                    # with val = 0/1 the channellist can be clicked throu
                    # get actual channel id
                    channelid = int(self.radioData['CURRENT_ID'])
                    if value == True:
                        # addieren
                        if channelid < 8:
                            channelid = channelid + 1
                        elif channelid == 8:
                            channelid = 1
                    elif value == False:
                        # subdrahieren
                        if channelid > 1:
                            channelid = channelid-1
                        elif channelid == 1:
                            channelid = 8
                    msg = 'PLAY\r\nSTATION:'+str(channelid)
                pass
            else:
                self.logger.debug("RadioInet: Command not supported!")
                msg = ""

            # BUILD MESSAGE TOGETHER!
            if msg != "":
                return "COMMAND:" + msg + "\r\nID:" + self._name + "\r\n\r\n"

        except Exception as e:
            self.logger.debug("RadioInet: Could not Build Message{}".format(e))

    def msgDecryptor(self, msg):
        """
        Decrypt a given UDP message from the Radio
        :msg from Socket Server
        """
        channelList = []
        msgArray = msg.splitlines()
        self.logger.debug("RadioInet: Message Decryptor {}".format(msgArray))
        try:
            if not "NACK" in msgArray[-2]:
                if "GET" in msgArray[0]:
                    if self._name in msgArray[2]:
                        if msgArray[1] == 'ALL_STATION_INFO':
                            for i in range(1, 9):
                                channelList.append({'id': msgArray[3*i].split(':')[1], 'chan': msgArray[(
                                    3*i)+1].split(':')[1], 'url': msgArray[(3*i)+2][4:]})
                            for i2 in range(0, 8):
                                values = list(channelList[i2].values())
                                # self.radioData['id'+str(i2)] = values[0]
                                # self.radioData['chan'+str(i2)] = values[1]
                                # self.radioData['url'+str(i2)] = values[2]
                                self.radioData['id'+str(i2+1)] = values[0]
                                self.radioData['s'+str(i2+1)] = values[2]
                                self.radioData['n'+str(i2+1)] = values[1]
                            #print("sender", channelList)
                            # aufteilen auf die einzelnen senderitems1
                            self.logger.debug(
                                "RadioInet: Sender{}".format(channelList))

                        elif msgArray[1] == 'PLAYING_MODE':
                            if 'PLAYING STOPPED' in msgArray[3]:
                                self.logger.debug("RadioInet: not Playing")

                            else:
                                playingmode = {'playmode': msgArray[3].split(':')[1], 'id': msgArray[4].split(
                                    ':')[1], 'chan': msgArray[5].split(':')[1], 'url': msgArray[6][4:]}
                                self.logger.debug(
                                    "RadioInet: Mode{}".format(playingmode))
                                #print("Mode", playingmode)
                                self.radioData['CURRENT_ID'] = playingmode['id']
                                self.radioData['CURRENT_NAME'] = playingmode['chan']
                                self.radioData['CURRENT_URL'] = playingmode['url']

                        elif msgArray[1] == 'VOLUME':
                            vol = {'vol': msgArray[3].split(':')[1]}
                            #print("VOLUME", vol)
                            self.logger.debug(
                                "RadioInet: VOLUME {}".format(vol))
                            volume = floor((int(vol['vol'])*3.22))
                            self.radioData['VOLUME'] = volume
                            pass

                        elif msgArray[1] == 'POWER_STATUS':
                            energy = {'power_status': msgArray[3].split(
                                ':')[1], 'energy_mode': msgArray[4].split(':')[1]}
                            #print("Power Status", energy)
                            self.logger.debug(
                                "RadioInet: Power status {}".format(energy))
                            if energy['power_status'] == 'ON':
                                self.radioData['POWER'] = True
                                self.radioData['POWER_STATUS'] = True
                                # when radio  returning is playing, then read Volume, all stations
                                self.sendCommand(self.msgBuilder('VOLUME'))
                                # if self.radioData['s1'] == '' or self.radioData['s2'] == '' or self.radioData['s3'] == '' or self.radioData['s4'] == '':
                                self.sendCommand(
                                    self.msgBuilder('ALL_STATION_INFO'))
                                pass
                            elif energy['power_status'] == 'OFF':
                                self.radioData['POWER'] = False
                                self.radioData['POWER_STATUS'] = False
                                pass
                        else:
                            self.logger.debug(
                                "RadioInet: NACK {}".format(msgArray))

                elif "SET" in msgArray[0]:
                    print("RadioINet: MSG from Radio", msgArray)
                    if msgArray[1] == 'VOLUME_ABSOLUTE':
                        vol = {'vol': msgArray[1].split(':')[1]}
                        #print("VOLUME", vol)
                        self.logger.debug("RadioInet: VOLUME {}".format(vol))
                        self.radioData['VOLUME'] = vol['vol']
                        pass
                elif "PLAYMODE" in msgArray[0]:
                    print("RadioINet: MSG from Radio", msgArray)
                    self.radioData['VOLUME'] = vol['vol']
                elif "PLAY" in msgArray[0]:
                    print("RadioINet: MSG from Radio", msgArray)
                    self.sendCommand(self.msgBuilder('PLAYING_MODE'))
                elif "SAVE" in msgArray[0]:
                    print("RadioINet: MSG from Radio", msgArray)

                elif "NOTIFICATION" in msgArray[0]:
                    event = msgArray[3].split(':')[1]
                    self.logger.debug(
                        "RadioINet: Notification MSG from Radio", msgArray)

                    if event == 'VOLUME_CHANGED':
                        # read new volume
                        self.logger.debug(
                            "RadioInet: VOLUME changed MSG from Radio", msgArray)
                        self.sendCommand(self.msgBuilder('VOLUME'))
                    elif event == 'SYSTEM_BOOTED':
                        # init read of all data
                        self.logger.debug(
                            "RadioInet: System booted MSG from Radio", msgArray)
                        self.sendCommand(self.msgBuilder('ALL_STATION_INFO'))
                    elif event == 'POWER_ON':
                        # init read of all data
                        self.logger.debug(
                            "RadioInet: Power ON MSG from Radio", msgArray)
                        self.radioData['POWER_STATUS'] = True
                        self.sendCommand(self.msgBuilder('ALL_STATION_INFO'))

                        # when poweron and "RED_ACT" = True => send "VOL_RED" to radio
                        if self.radioData['RED_ACT'] == True:
                            self.sendCommand(self.msgBuilder(
                                'VOL_ABS', self.radioData['VOL_RED']))

                    elif event == 'POWER_OFF':
                        # init read of all data
                        self.logger.debug(
                            "RadioInet: POWER OFF MSG from Radio", msgArray)
                        self.radioData['POWER_STATUS'] = False
                    elif event == 'STATION_CHANGED':
                        # init read new station
                        self.logger.debug(
                            "RadioInet: Station changed MSG from Radio", msgArray)
                        self.sendCommand(self.msgBuilder('PLAYING_MODE'))
                        self.sendCommand(self.msgBuilder('ALL_STATION_INFO'))
                    elif event == 'URL_IS_PLAYING':
                        # init read url of playing station
                        self.logger.debug(
                            "RadioInet: System booted MSG from Radio", msgArray)
                        self.sendCommand(self.msgBuilder('PLAYING_MODE'))
            else:
                print("NACK")
            print("radioDATA", self.radioData)
        except Exception as e:
            self.logger.debug("RadioInet: Cannot Decrypt Message{}".format(e))

        # items immer nach nachricht von Radio updaten
        self.update_items()

    def UDPServer(self):
        """
        Creates a Socket Server to recieve Messages from the Radio
        """
        port = 4242
        self.logger.debug("RadioInet: Open Udp Server port")
        # Create Datagram Socket (UDP)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Allow incoming broadcasts
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 5)
            s.setblocking(True)  # Set socket to non-blocking mode
            s.bind(('', port))  # Accept Connections on port
            while True:
                # Buffer size is 8192. Change as needed.
                message, adress = s.recvfrom(2048)
                #self.logger.debug("RadioInet: msg recv {}".format(message.decode()))
                self.msgDecryptor(message.decode())
        except Exception as e:
            self.logger.debug(
                "RadioInet: UDP Server Cannot connect.{}".format(e))

# ------------------------------------------
#    Webinterface Methoden
# ------------------------------------------

    def get_connection_info(self):
        info = {}
        info['ip'] = self._ip
        info['name'] = self._name
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
            self.logger.error(
                "Plugin '{}': Not initializing the web interface".format(self.get_shortname()))
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

        self.logger.debug("Plugin Debug ausgabe '{0}': {1}, {2}, {3}, {4}, {5}".format(self.get_shortname(
        ), webif_dir, self.get_shortname(), config,  self.get_classname(), self.get_instance_name()))
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
            if ('radioInet' in item.conf):
                plgitems.append(item)
                self.logger.debug("Plugin : Render index Webif")
        tmpl = self.tplenv.get_template('index.html')
        return tmpl.render(plugin_shortname=self.plugin.get_shortname(),
                           plugin_version=self.plugin.get_version(),
                           plugin_info=self.plugin.get_info(),
                           p=self.plugin,
                           connection=self.plugin.get_connection_info(),
                           webif_dir=self.webif_dir,
                           items=sorted(plgitems, key=lambda k: str.lower(k['_path'])))
