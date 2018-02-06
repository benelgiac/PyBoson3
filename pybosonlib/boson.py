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
from pyboson.pybosonlib.flirprotocols import Frame, Fbp
from time import sleep
import struct
from collections import OrderedDict

class Boson():
        
    # Format: Command Hex Code, Byte Size (command, response, get, set)
    COMMANDS = {
        'GETSERIAL'           :    { 'id': bytearray([0x00, 0x05, 0x00, 0x02]), 'retbytes': 4},
        'GETCOLORLUT'         :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x04]), 'retbytes': 4, 'type': 'int'},
        'SETCOLORLUT'         :    { 'id': bytearray([0x00, 0x0B, 0x00, 0x03]), 'retbytes': 0},
        'GETPARTNUMBER'       :    { 'id': bytearray([0x00, 0x05, 0x00, 0x04]), 'retbytes': 20},
        'GETGAINMODE'         :    { 'id': bytearray([0x00, 0x05, 0x00, 0x15]), 'retbytes': 4, 'type': 'int'},
        'SETGAINMODE'         :    { 'id': bytearray([0x00, 0x05, 0x00, 0x14]), 'retbytes': 0},
        'ACGSETLINEARPERCENT' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x03]), 'retbytes': 0},
        'ACGGETLINEARPERCENT' :    { 'id': bytearray([0x00, 0x09, 0x00, 0x04]), 'retbytes': 4, 'type': 'float'},
        'ACGGETOUTLIERCUT'    :    { 'id': bytearray([0x00, 0x09, 0x00, 0x06]), 'retbytes': 4, 'type': 'float'},
        'ACGSETOUTLIERCUT'    :    { 'id': bytearray([0x00, 0x09, 0x00, 0x05]), 'retbytes': 0},
        'ACGGETMAXGAIN'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x0A]), 'retbytes': 4, 'type': 'float'},
        'ACGSETMAXGAIN'       :    { 'id': bytearray([0x00, 0x09, 0x00, 0x09]), 'retbytes': 0},
        'ACGRESTOREDEFAULT'   :    { 'id': bytearray([0x00, 0x05, 0x00, 0x1B]), 'retbytes': 0},
    }
    
    LUT = OrderedDict([
        (0x00000000   , 'WHITEHOT'),
        (0x00000001   , 'BLACKHOT'),
        (0x00000002   , 'RAINBOW'),
        (0x00000003   , 'RAINBOW_HC'),
        (0x00000004   , 'IRONBOW'),
        (0x00000005   , 'LAVA'),
        (0x00000006   , 'ARCTIC'),
        (0x00000007   , 'GLOBOW'),
        (0x00000008   , 'GRADEDFIRE'),
        (0x00000009   , 'HOTTEST'),
    ])
    
    GAINMODE = OrderedDict([
        (0x00000000   , 'HIGH GAIN'),
        (0x00000001   , 'LOW GAIN'),
        (0x00000002   , 'AUTO GAIN'),
        (0x00000003   , 'DUAL GAIN'),
        (0x00000004   , 'MANUAL GAIN'),
    ])
    
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
    def getDataFromReply(self, reply, commandname):
        _type = None
        length = self.COMMANDS[commandname]['retbytes']
        if 'type' in self.COMMANDS[commandname]:
            _type = self.COMMANDS[commandname]['type']
        
        end = -3
        start = end-length
        if _type == 'int':
            return struct.unpack('>i',reply[start:end])[0]
        elif _type == 'float':
            return struct.unpack('>f',reply[start:end])[0]
        else:
            return reply[start:end]
    
    def sendCmdAndGetReply(self, commandname, data = bytearray()):
        retdata = b''
        reply = self.send_packet(self._construct_cmd(commandname, data))
        if self.COMMANDS[commandname]['retbytes']==4:
             retdata = self.getDataFromReply(reply, commandname)
        elif self.COMMANDS[commandname]['retbytes']!=0:
             retdata = self.getDataFromReply(reply, commandname)

        #import pdb;pdb.set_trace()
        return retdata

    #---------- Methods supposed to be invoked from users --------------
    def getSerial(self):
        return self.sendCmdAndGetReply('GETSERIAL')
    
    def getColorLut(self):
        return self.LUT[self.sendCmdAndGetReply('GETCOLORLUT')]
        
    def getPartNumber(self):
        return self.sendCmdAndGetReply('GETPARTNUMBER')
        
    def setColorLut(self, lutstring):
        return self.sendCmdAndGetReply('SETCOLORLUT', ToByteArray(_getKeyFromValue(self.LUT, lutstring)))
        
    def getGainState(self):
        return self.GAINMODE[self.sendCmdAndGetReply('GETGAINMODE')]
        
    def setGainState(self, gainstring):
        return self.sendCmdAndGetReply('SETGAINMODE', ToByteArray(_getKeyFromValue(self.GAINMODE, gainstring)))
        
    def getAcgLinearPercent(self):
        return self.sendCmdAndGetReply('ACGGETLINEARPERCENT')
    
    def getAcgOutlierCut(self):
        return self.sendCmdAndGetReply('ACGGETOUTLIERCUT')    

    def getAcgMaxGain(self):
        return self.sendCmdAndGetReply('ACGGETMAXGAIN')        
        
    def setAcgMaxGain(self, value):
        return self.sendCmdAndGetReply('ACGSETMAXGAIN', ToByteArray(value))
        
    def setLinearPercent(self, value):
        return self.sendCmdAndGetReply('ACGSETLINEARPERCENT', ToByteArray(value))
        
    def setOutlierCut(self, value):
        return self.sendCmdAndGetReply('ACGSETOUTLIERCUT', ToByteArray(value))
        
    def restoreDefaults(self):
        return self.sendCmdAndGetReply('ACGRESTOREDEFAULT')
        
    def test_LUT(self):
        print ('Part number is %s' % self.getPartNumber())
        sleep(1)

        for data , lutstring in self.LUT.items():
            self.setColorLut(lutstring)
            sleep(1)
            print ('LUT is %s' % self.getColorLut())
            sleep(1)
        return 

#---------- Utility functions ---------------
def _getKeyFromValue(_d, _value):
    for k,v in _d.items():
        if v==_value:
            return k
    return None

def ToByteArray(_i):
    frmt = ''
    if isinstance(_i, int):
        frmt = '>i'
    elif isinstance(_i, float):
        frmt = '>f'
    else:
        assert(True)
    
    return struct.pack(frmt,_i)
