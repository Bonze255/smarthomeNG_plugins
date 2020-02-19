"""
Sample program for hikvision api.
"""

import json
import sys
import time
import base64
from base64 import b64decode
import struct
from Crypto.Cipher import ChaCha20_Poly1305
import nacl.pwhash
def UDPParser():
       
    #payload = b'\xde\xad\xbe\x01\x00\x00\x00\x04\x00\x00 \x004\xc7\xb2\xec\x08}\xfd\xda\xa4%\xf9&\xf9\x02\xb7\x07\xbb;|\xf22\x17\xf4\x88\xc1\xb5\xd3\x13\xd6.\x8f;\n\x8e`(\xd5\x1c\xf7"\x7f\xbc\x08\xd5d\x88\xd4\x9b\xd01\xa39\x85=\xc7\xc6\xb6:'
    
    payload = b'\xDE\xAD\xBE\x01\x00\x00\x00\x04\x00\x00\x20\x00\x77\x35\x36\xDC\xC3\x0E\x2E\x84\x7E\x0E\x75\x29\xE2\x34\x60\xCF\xE3\xFF\xCC\x52\x3F\x37\xB2\xF2\xDC\x1A\x71\x80\xF2\x9B\x2E\xA0\x27\xA9\x82\x41\x9C\xCE\x45\x9D\x27\x45\x2E\x42\x14\xBE\x9C\x74\xE9\x33\x3A\x21\xDB\x10\x78\xB9\xF6\x7B'

    ident =     payload[:3]     #3  \xDE\xAD\xBE
    base64_bytes = base64.b64encode(ident)
    base64_message = base64_bytes.decode('ascii')
    print(base64_message) #ergibt 3q2+!
    version =   payload[3]      #1  \x01
    #opslimit =  payload[4:8]    #4  \x00\x00\x00\x04
    #memlimit =  payload[8:12]   #4  \x00\x00\x20\x00
    salt =      bytes(payload[12:28])  #16 \x77\x35\x36\xDC\xC3\x0E\x2E\x84\x7E\x0E\x75\x29\xE2\x34\x60\xCF
    nonce =     bytes(payload[28:36])  #8  \xE3\xFF\xCC\x52\x3F\x37\xB2\xF2
    ciphertext = bytes(payload[36:70])   #34 \xDC\x1A\x71\x80\xF2\x9B\x2E\xA0\x27\xA9\x82\x41\x9C\xCE\x45\x9D\x27\x45\x2E\x42\x14\xBE\x9C\x74\xE9\x33\x3A\x21\xDB\x10\x78\xB9\xF6\x7B
    username = 'foobar0001'#'ghevnh0003'##'ghevnh0003'
    password = b'QzT3jeK3JY'#'7vf9CMkU4h'##
    mlimit = 8192
    oplimit = 4

    #pw_to_stretch = 
    print('ident' , ident,'|','version ',version,'|','opslimit ',oplimit,'|','memlimit ',mlimit,'|','salt ', salt,'|','nonce ', nonce,'|','cipher', ciphertext)

    print('ident', struct.unpack(">3sBll16s8s34s",payload))
    #strech passwort 
    streched = nacl.pwhash.argon2i.kdf(32,password[:5], salt, opslimit=oplimit, memlimit=mlimit,encoder=nacl.encoding.RawEncoder)
    #print("streched - ", streched)
    #streched = self.stretchPassword(password[:5], salt, oplim, mem)
    #streched = '68bc1bbc629fd2ca6beb61accedf28ea'
    #streched = b'\x66\x6F\x6F\x62\x61\x72\x31\x30\x32\x20\x20\x20\x20\x20\x5A\x12\xE4\x13'
    #nonce = b'\xE3\xFF\xCC\x52\x3F\x37\xB2\xF2'
    #ciphertext = b'\xDC\x1A\x71\x80\xF2\x9B\x2E\xA0\x27\xA9\x82\x41\x9C\xCE\x45\x9D\x27\x45\x2E\x42\x14\xBE\x9C\x74\xE9\x33\x3A\x21\xDB\x10\x78\xB9\xF6\x7B'
    cipher = ChaCha20_Poly1305.new(key=streched, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    print(plaintext)
        
def stretchPassword(pw, salt, oplim, mem):
    if oplim == None:
        oplim = nacl.pwhash.argon2i.OPSLIMIT_INTERACTIVE
    if mem == None:
        mem = nacl.pwhash.argon2i.MEMLIMIT_MIN  
    return nacl.pwhash.argon2i.kdf(len(pw), pw, salt, opslimit=oplim, memlimit=mem)

UDPParser()
