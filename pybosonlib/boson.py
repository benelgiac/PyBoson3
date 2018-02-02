#! /usr/bin/env python
# -*- coding: utf8 -*-
#
#    PyVisca-3 Implementation of the Boson commands in python3
#
#    Author: Giacomo Benelli benelli.giacomo@aerialtronics.com
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, version 2 only.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
#    USA

"""PyBoson-3 by Giacomo Benelli <benelli.giacomo@gmail.com>"""

import serial,sys
from _thread import allocate_lock
from pybosonlib.flirprotocols import Frame, Fbp
from time import sleep
import struct

class Boson():
        
    # Format: Command Hex Code, Byte Size (command, response, get, set)
    COMMANDS = {
        'GETSERIAL'      :    { 'id': bytearray([0x00, 0x05, 0x00, 0x02]), 'retbytes': 4},
        'GETCOLORLUT'    :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x04]), 'retbytes': 4},
        'SETCOLORLUT'    :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x03]), 'retbytes': 0},
        'GETPARTNUMBER'  :    { 'id': bytearray([0x00, 0x05, 0x00, 0x04]), 'retbytes': 20},

    }
    
    LUT = {
        0x00000000   : 'WHITEHOT',
        0x00000001   : 'BLACKHOT',
        0x00000002   : 'RAINBOW',
        0x00000003   : 'RAINBOW_HC',
        0x00000004   : 'IRONBOW',
        0x00000005   : 'LAVA',
        0x00000006   : 'ARCTIC',
        0x00000007   : 'GLOBOW',
        0x00000008   : 'GRADEDFIRE',
        0x00000009   : 'HOTTEST',
    }
    
    #---------- Methods related to serial port handling ---------------
    def __init__(self,portname="/dev/ttyACM0", timeout=1):
        self.serialport=None
        self.mutex = allocate_lock()
        self.portname=portname
        self.open_port(timeout)

    def open_port(self, timeout):

        self.mutex.acquire()

        if (self.serialport == None):
            try:
                self.serialport = serial.Serial(self.portname,921600,timeout=timeout,stopbits=1,bytesize=8,rtscts=False, dsrdtr=False)
                self.serialport.flushInput()
            except Exception as e:
                print ("Exception opening serial port '%s' for display: %s\n" % (self.portname,e))
                raise e
                self.serialport = None
        
        self.serialport.reset_input_buffer()
        self.serialport.reset_output_buffer()

        self.mutex.release()

    def dump(self,packet,title=None):
        if not packet or len(packet)==0:
            return

        print ('%s: %s' % (title,packet))


    def recv_packet(self,extra_title=None):
        # read up to 32 bytes until 0xff
        packet=b''
        count=0
        while count<64:
            s=self.serialport.read(1)
            if s:
                count+=1
                packet=packet+bytes(s)
            else:
                import pdb;pdb.set_trace()
                print ("ERROR: Timeout waiting for reply")
                break
            if s==b'\xae':
                break

        if extra_title:
            self.dump(packet,"recv: %s" % extra_title)
        else:
            self.dump(packet,"recv")
        return packet

    def _write_packet(self,packet):

        if not self.serialport.isOpen():
            sys.exit(1)

        # lets see if a completion message or someting
        # else waits in the buffer. If yes dump it.
        if self.serialport.inWaiting():
            self.recv_packet("ignored")

        self.dump (packet, 'Sending packet')
        self.serialport.write(packet)
        
    def send_packet(self, packet):

        self.mutex.acquire()

        self._write_packet(packet)

        reply = self.recv_packet()

        self.mutex.release()

        return reply
    
    #---------- Using Frame and Fbp to assemble packet ---------------
    def _construct_cmd(self, _command_name, _data = bytearray()):
        payload = Fbp(self.COMMANDS[_command_name]['id'], _data)
        
        frame = Frame(payload.raw())
        
        serial_cmd = frame.raw()
        return serial_cmd
        
    ####### Poor man's data extractor. Won't work always because of
    # byte stuffing. Just use for test/debug purposes
    def getDataFromReply(self, reply, lenght=4, toint=True):
        end = -3
        start = end-lenght
        if toint == True:
            return struct.unpack('>I',reply[start:end])[0]
        else:
            return reply[start:end]
    
    def sendCmdAndGetReply(self, commandname, data = bytearray()):
        retdata = b''
        reply = self.send_packet(self._construct_cmd(commandname, data))
        if self.COMMANDS[commandname]['retbytes']==4:
             retdata = self.getDataFromReply(reply, self.COMMANDS[commandname]['retbytes'],toint=True)
        elif self.COMMANDS[commandname]['retbytes']!=0:
             retdata = self.getDataFromReply(reply, self.COMMANDS[commandname]['retbytes'],toint=False)
        return retdata

    #---------- Methods supposed to be invoked from users --------------
    def getSerial(self):
        return self.sendCmdAndGetReply('GETSERIAL')
    
    def getColorLut(self):
        return self.sendCmdAndGetReply('GETCOLORLUT')
        
    def getPartNumber(self):
        return self.sendCmdAndGetReply('GETPARTNUMBER')
        
    def setColorLut(self, lutstring):
        return self.sendCmdAndGetReply('SETCOLORLUT', _intToByteArray(_getKeyFromValue(self.LUT,lutstring)))
        
    def test_LUT(self):
        print ('Part number is %s' % self.getPartNumber())
        sleep(1)

        for data , lutstring in self.LUT.items():
            self.setColorLut(lutstring)
            sleep(1)
            print ('LUT is %s' % self.LUT[self.getColorLut()])
            sleep(1)
        return 

#---------- Utility functions ---------------
def _getKeyFromValue(_d, _value):
    for k,v in _d.items():
        if v==_value:
            return k
    return None

def _intToByteArray(_i):
    assert (isinstance(_i, int))
        
    _b1 = bytearray([(_i&0xFF000000) >> 24])
    _b2 = bytearray([(_i&0x00FF0000) >> 16])
    _b3 = bytearray([(_i&0x0000FF00) >> 8])
    _b4 = bytearray([(_i&0x000000FF) ])
    return _b1+_b2+_b3+_b4
