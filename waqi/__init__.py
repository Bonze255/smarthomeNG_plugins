import os
import json 

import requests
class WAQI():
    #http://flothesof.github.io/world-air-quality-pollution-maps.html
    def __init__(self):
        self.base_url = "https://api.waqi.info"
        self.token = "ae2c2b905e7bddc91c967a5a4ea9d6cdc757f9cb"
        self.city = 'germany/rheinlandpfalz/kaiserslautern-rathausplatz'
        self.getData()
        
    def getData(self):
        r = requests.get(self.base_url + f"/feed/"+self.city+"/?token="+self.token)
        if r.status_code == 200:
            print(r.json())
            aqi_data = r.json()['data']['iaqi']
            self._data['waqi_no2'] = r.json()['data']['iaqi']['no2']['v']
            self._data['waqi_o3'] = r.json()['data']['iaqi']['o3']['v']
            self._data['waqi_p'] = r.json()['data']['iaqi']['p']['v']
            self._data['waqi_pm10'] = r.json()['data']['iaqi']['pm10']['v']
            self._data['waqi_t'] = r.json()['data']['iaqi']['t']['v']
            
            print(r.json()['data']['iaqi'])
            print("no2 ",r.json()['data']['iaqi']['no2']['v'])
            print("o3 ",r.json()['data']['iaqi']['o3']['v'])
            print("p ",r.json()['data']['iaqi']['p']['v'])
            print("pm10 ",r.json()['data']['iaqi']['pm10']['v'])
            print("t ",r.json()['data']['iaqi']['t']['v'])
            print("time ",r.json()['data']['time']['v'])
            #{'no2': {'v': 9.6}, 'o3': {'v': 17.9}, 'p': {'v': 1028.9}, 'pm10': {'v': 3}, 't': {'v': 1.6}}
            #print("City: {}, Air quality index: {}".format(r.json()['data']['city']['name'], r.json()['data']['aqi']))
        else:
            print("Fehler bei der Datenabfrage")

WAQI()



 # 'aqi':3,
   # 'idx':6133,
   # 'attributions':[
      # {
         # 'url':'http://www.luft-rlp.de/aktuell/',
         # 'name':'Luftreinhaltung Rheinland-Pfalz',
         # 'logo':'Germany-RheinlandPfalz.png'
        # },
      # {
         # 'url':'https://waqi.info/',
         # 'name':'World Air Quality Index Project'
      
        # }
   
    # ],
   # 'city':{
      # 'geo':[
         # 49.446,
         # 7.7673
      
# ],
      # 'name':'Kaiserslautern-Rathausplatz, Germany',
      # 'url':'https://aqicn.org/city/germany/rheinlandpfalz/kaiserslautern-rathausplatz'
   
# },
   # 'dominentpol':'pm10',
   # 'iaqi':{
      # 'no2':{
         # 'v':9.6
      
# },
      # 'o3':{
         # 'v':17.9
      
# },
      # 'p':{
         # 'v':1028.9
      
# },
      # 'pm10':{
         # 'v':3
      
# },
      # 't':{
         # 'v':1.6
      
# }
   
# },
   # 'time':{
      # 's':'2020-02-21 08:00:00',
      # 'tz':'+01:00',
      # 'v':1582272000
   
# },
   # 'debug':{
      # 'sync':'2020-02-21T16:13:37+09:00'
   
# }
# }
