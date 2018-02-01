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
from flirprotocols import Frame, Fbp
from time import sleep
import struct

class Boson():
    
    # Format: Command Hex Code, Byte Size (command, response, get, set)
    COMMANDS = {
        'GETSERIAL'      :    bytearray([0x00, 0x05, 0x00, 0x02]),
        'GETCOLORLUT'    :    bytearray([0x00, 0x0B, 0x00, 0x04]),
        'SETCOLORLUT'    :    bytearray([0x00, 0x0B, 0x00, 0x03])
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
        # read up to 16 bytes until 0xff
        packet=b''
        count=0
        while count<32:
            s=self.serialport.read(1)
            if s:
                count+=1
                packet=packet+bytes(s)
            else:
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
        
    def _construct_cmd(self, _command_name, _data = bytearray()):
        payload = Fbp(self.COMMANDS[_command_name], _data)
        
        frame = Frame(payload.raw())
        
        serial_cmd = frame.raw()
        return serial_cmd
        
    ####### Poor man's data extractor. Won't work always because of
    # byte stuffing. Just use for test/debug purposes
    def getDataFromReply(self, reply):
        return struct.unpack('>I',reply[-7:-3])[0]
        
    ############ Functions ########################
    def getSerial(self):
        return self._construct_cmd('GETSERIAL')
    
    def getColorLut(self):
        return self._construct_cmd('GETCOLORLUT')
        
    def setColorLut(self, data):
        return self._construct_cmd('SETCOLORLUT', data)
        
    def test_LUT(self):
        #import pdb;pdb.set_trace()
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x01]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x02]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x03]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x04]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x05]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x06]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x07]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        sleep(1)
        _cmd = self.setColorLut(bytearray([0x00, 0x00, 0x00, 0x08]))
        self.send_packet(_cmd)
        sleep(1)
        _cmd = self.getColorLut()
        reply = self.send_packet(_cmd)
        print ('LUT is %s' % self.LUT[self.getDataFromReply(reply)])
        #print ('Built command %s' %(_cmd))
        return 
        
