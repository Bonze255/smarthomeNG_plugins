import urllib
#import doorbirdpy
import os
import threading
import socket
import binhex
import sys
import struct
import base64
import json
import sys
import time
import base64
from base64 import b64decode
import struct
from Crypto.Cipher import ChaCha20_Poly1305
import nacl.pwhash



class Dbird:
    def __init__(self):
        self._ip = '192.168.178.94'
        self._username = 'ghevnh0003'
        self._password = ''
        #UDP SERVER THREAD
        self.UDPServerThread = threading.Thread(target = self.UDPServer)
        self.UDPServerThread.start()
    
    
    def decrypt(self, payload):
        if len (payload) >60:
            ident, version,oplimit,mlimit,salt,nonce,ciphertext =  struct.unpack(">3sBll16s8s34s",payload)
            
            #ident =     payload[:3]     #3  \xDE\xAD\xBE
            base64_bytes = base64.b64encode(ident)
            base64_message = base64_bytes.decode('ascii')
            print(base64_message) #ergibt 3q2+!
            if base64_bytes.decode('ascii') == '3q2+':
                streched = nacl.pwhash.argon2i.kdf(32,self._password[:5], salt, opslimit=oplimit, memlimit=mlimit,encoder=nacl.encoding.RawEncoder)
                cipher = ChaCha20_Poly1305.new(key=streched, nonce=nonce)
                plaintext = cipher.decrypt(ciphertext)
                
                decryped_user = plaintext[:6]
                decryped_doorbellnumber = plaintext[7:14]
                timestamp = plaintext[14:20]
                print(decryped_user, decryped_doorbellnumber, timestamp)
                if user == self.username[:6]:
                    return True
                else:
                    return False
            else:
                print("Falscher Header")
                return False
        
    def UDPServer(self):
        port = 35344 #alternativ 35344
        ip=''
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)    # Create Datagram Socket (UDP)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 5) # Allow incoming broadcasts
        s.setblocking(True) # Set socket to non-blocking mode
        s.bind(('', port)) #Accept Connections on port
        while True:
            try:
                message, address = s.recvfrom(1024) # Buffer size is 8192. Change as needed.
                print('message raw',message)
                #print('message decoded',message.decode("utf-8"))
                self.decrypt(message)
            except Exception as e:
                print("Doorbird: UDP Server Cannot connect.",e)
            finally:
                s.close()
doorbird1 = Dbird()
