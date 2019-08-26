import pyads
import sched
import time

class ADSCommunication:
    def setRoute(self):
        #ONLY ON LINUX!
        SENDER_AMS = '1.2.3.4.1.1'
        PLC_IP = '192.168.0.100'
        USERNAME = 'user'
        PASSWORD = 'password'
        ROUTE_NAME = 'RouteToMyPC'
        HOSTNAME = 'MyPC'
        PLC_AMS_ID = '11.22.33.44.1.1'
        pyads.add_route_to_plc(SENDER_AMS, HOSTNAME, PLC_IP, USERNAME, PASSWORD, route_name=ROUTE_NAME)
    #ONLY Linux
    def connectLinux(self):
        remote_ip = '192.168.0.100'
        remote_ads = '5.12.82.20.1.1'
        with pyads.Connection(remote_ads, pyads.PORT_SPS1, remote_ip) as plc:
            plc.read_by_name('.TAG_NAME', pyads.PLCTYPE_INT)
     
    def connect(self, _ip, _port):
        try:
            self.plc = pyads.Connection(_ip, _port)
            self.plc.open()
        except e as Exception:
            print(e)
    def disconnect(self):
        self.plc.close()
    def read(self, _datatype):
        ret = self.plc.read_by_name('Main.drehgeber_a', pyads.PLCTYPE_INT)
        print(ret)
        ret = self.plc.read_by_name('Main.drehgeber_x', pyads.PLCTYPE_INT)
        print(ret)
        ret = self.plc.read_by_name('Main.drehgeber_y', pyads.PLCTYPE_INT)
        print(ret)
    def write(self, _value):
        if isinstance(_value, Boolean):
            datatype = pyads.PLCTYPE_BOOL
        elif isinstance(_value, int):
            datatype = pyads.PLCTYPE_INT
        elif isinstance(_value, float):
            datatype = pyads.PLCTYPE_REAL

        ret = self.plc.write_by_name('Main.I1', datatype)
    #plc.read_by_name('MAIN.drehgeber_y', pyads.PLCTYPE_INT)
    #plc.read_by_name('MAIN.drehgeber_z', pyads.PLCTYPE_INT)

    #plc.write_by_name('global.bool_value', False, pyads.PLCTYPE_BOOL)
    #plc.read_by_name('global.bool_value', pyads.PLCTYPE_BOOL)

    def __init__(self):
        self.ip = '5.62.167.90.1.1'
        self.port = 851
        self.connect(self.ip, self.port)
        self.s = sched.scheduler(time.time, time.sleep)
        self.cycle()
        
        #self.disconnect()
        #self.plc= None
    def cycle(self):
        self.read('BOOL')
        self.s.enter(1, 1, self.cycle)
        self.s.run()
test = ADSCommunication()
